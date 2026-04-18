  1. What is a database connection vs. a session?

  Think of it this way:

  - A connection is the raw TCP pipe to Postgres. It carries one active transaction at a time.
  - A session is an ORM object that sits on top of a connection and lets you work with Python objects (your WeatherQuery model) instead of raw
  SQL.

  In conftest.py:77-82:

  async with db_engine.connect() as conn:   # <-- opens one raw connection
      await conn.begin()                    # <-- starts a transaction on it
      session = AsyncSession(bind=conn, ...)# <-- session is bound TO that connection
      yield session
      await session.close()
      await conn.rollback()                 # <-- rolls back the transaction

  The key word is bind=conn. You are telling SQLAlchemy: "do not open a new connection; use this specific one I give you." That binding is what
  makes everything below work.

  ---
  2. What does session.commit() normally do?

  In the normal world (outside tests), a session manages its own connection pool. When you call session.commit(), it:

  1. Flushes all pending changes (turns Python object mutations into SQL INSERT/UPDATE)
  2. Sends COMMIT to Postgres — permanently writing data to disk
  3. Releases the connection back to the pool

  This is the behavior you see in production code at weather_repo.py:48:

  await self._session.commit()  # in production: real commit to DB

  ---
  3. What does session.commit() do when the session is bound to a connection?

  Here is the subtle part. When the session is bound to an existing connection (as in your fixture), session.commit() does something different:

  - It flushes pending changes (SQL INSERT is sent over the wire)
  - It does not send COMMIT to Postgres
  - It releases a "savepoint" instead (SQLAlchemy creates internal savepoints automatically in this mode)

  So in test_cities_hits.py:23:

  db_session.add(record)
  await db_session.commit()   # flushes INSERT to the connection — but outer transaction stays open
  await db_session.refresh(record)  # reads back the auto-generated id from the DB

  The row exists inside the connection's transaction, but it has not been committed to Postgres. It is "visible within this transaction" only.

  ---
  4. Why can db_async_client see the row?

  Look at conftest.py:50-57:

  async def db_async_client(db_session: AsyncSession, ...) -> AsyncGenerator[AsyncClient]:
      async def _override_db_session() -> AsyncGenerator[AsyncSession]:
          yield db_session   # <-- the SAME session object

      app.dependency_overrides[get_db_session] = _override_db_session

  When your endpoint handler calls get_db_session, FastAPI's DI resolves it to _override_db_session, which yields the exact same db_session
  object — the one bound to the same connection where the INSERT was flushed.

  So when your endpoint runs a SELECT query, it goes through the same connection, sees the same open transaction, and finds the Paris row. This
  is called read-your-own-writes within a transaction.

    connection (transaction open)
    ├── paris_query fixture: INSERT flushed here
    ├── db_session: bound to this connection
    └── db_async_client: wires the same db_session → endpoint SELECT sees the INSERT

  If you had used async_client instead (which uses a MagicMock session), the endpoint would never touch the real connection, and the row would be
   invisible.

  ---
  5. What happens at teardown?

  After each test, control returns to conftest.py:81-82:

  await session.close()
  await conn.rollback()   # <-- the outer transaction is rolled back

  conn.rollback() tells Postgres: "undo everything that happened in this transaction." The Paris row disappears from the database as if it was
  never there. The next test starts with a clean slate.

  This is the standard transaction-per-test rollback pattern. You get real DB behavior (real SQL, real constraints) without test pollution.

  ---
  6. Visual timeline for one test

  db_session fixture starts
  │  conn.begin()           → transaction T1 opens in Postgres
  │
  paris_query fixture runs
  │  session.add(record)    → Python object tracked
  │  session.commit()       → INSERT flushed to T1 (savepoint released internally)
  │                            row visible inside T1, not committed to disk
  │  session.refresh(record)→ SELECT auto-generated id — works because T1 is open
  │
  test body runs
  │  db_async_client sends POST /cities-cloud
  │  endpoint calls repo.get_cities_cloud(...)
  │  SELECT runs on the same session → same T1 → finds Paris row
  │  asserts pass ✓
  │
  db_session fixture teardown
     session.close()        → session released
     conn.rollback()        → T1 rolled back, Paris row gone
     next test starts fresh

  ---
  7. Should you change anything?

  No. The pattern is correct and idiomatic for SQLAlchemy integration tests. The only thing worth knowing for the future: if you ever add a
  fixture that creates its own engine/connection (not bound to db_session), it will not share the transaction and will not see the Paris row —
  that would be a bug.


  ----------------------------------


  ● Connections, Sessions, and Transactions — the full picture

  These are three different layers. Each one has a single responsibility.

  ---
  Layer 1 — Connection

  A connection is the raw TCP socket to Postgres. It speaks the Postgres wire protocol. It knows nothing about Python objects or ORM models — it
  only sends SQL strings and receives result rows.

  Your Python process          Postgres server
        │                            │
        │──── TCP socket ────────────│
        │       (this is the         │
        │        connection)         │

  Opening a connection is expensive (TCP handshake, auth, SSL). That is why engines maintain a connection pool — a set of pre-opened connections
  ready to be borrowed.

  # Under the hood when you call db_engine.connect():
  engine = create_async_engine("postgresql+asyncpg://...")
  # engine holds a pool of ~5 connections by default

  async with engine.connect() as conn:
      # conn is one connection borrowed from the pool
      # when the block exits, it goes back to the pool
      result = await conn.execute(text("SELECT 1"))

  A connection can only do one thing at a time — it processes SQL statements sequentially.

  ---
  Layer 2 — Transaction

  A transaction is a contract with Postgres. It says: "group these SQL statements together — either all succeed or all fail." It lives inside a
  connection.

  connection
  └── transaction (optional, but almost always present)
      ├── statement 1: INSERT ...
      ├── statement 2: UPDATE ...
      └── statement 3: SELECT ...   ← all or nothing

  You open a transaction with BEGIN, close it with COMMIT (save) or ROLLBACK (undo).

  async with engine.connect() as conn:
      await conn.begin()                           # sends BEGIN to Postgres
      await conn.execute(text("INSERT INTO ..."))  # buffered in the transaction
      await conn.execute(text("UPDATE ..."))       # also buffered
      await conn.commit()                          # sends COMMIT — both writes saved
      # OR:
      await conn.rollback()                        # sends ROLLBACK — both writes undone

  Postgres guarantees ACID properties for a transaction:
  - Atomic: all statements commit or none do
  - Consistent: constraints are checked at commit
  - Isolated: other connections don't see your uncommitted rows (by default)
  - Durable: once committed, data survives crashes

  ---
  Layer 3 — Session

  A session is a SQLAlchemy concept. Postgres has never heard of it. Its job is to be the bridge between Python objects and SQL. It tracks which
  objects you've loaded or modified, and translates those changes into SQL at the right moment.

  session (Python world)        connection (SQL world)
  ├── identity map              │
  │   ├── WeatherQuery(id=1)    │
  │   └── WeatherQuery(id=2)    │
  ├── pending adds/changes   ───┤──► flush → INSERT/UPDATE SQL
  └── queued deletes         ───┘

  The session has its own mini-lifecycle:

  ┌────────────────────┬───────────────────────────────────────────────────────────┐
  │   Session action   │                       What happens                        │
  ├────────────────────┼───────────────────────────────────────────────────────────┤
  │ session.add(obj)   │ object enters "pending" state — no SQL yet                │
  ├────────────────────┼───────────────────────────────────────────────────────────┤
  │ session.flush()    │ SQL is sent to the connection, but transaction stays open │
  ├────────────────────┼───────────────────────────────────────────────────────────┤
  │ session.commit()   │ flushes + commits the transaction                         │
  ├────────────────────┼───────────────────────────────────────────────────────────┤
  │ session.rollback() │ discards pending changes, rolls back transaction          │
  ├────────────────────┼───────────────────────────────────────────────────────────┤
  │ session.close()    │ detaches all objects, releases connection back to pool    │
  └────────────────────┴───────────────────────────────────────────────────────────┘

  ---
  The three layers together — normal production flow

  app handles GET /weather?city=Paris
  │
  ├── FastAPI calls get_db_session (conftest.py / database.py)
  │       │
  │       ├── engine lends a connection from the pool
  │       │       connection
  │       │       └── BEGIN (transaction T1 opens)
  │       │
  │       └── session = AsyncSession(connection)   ← session wraps the connection
  │
  ├── router calls repo.save(response)
  │       │
  │       ├── session.add(WeatherQuery(...))        ← object is "pending" in Python
  │       ├── session.commit()
  │       │       │
  │       │       ├── flush: sends INSERT to Postgres over the connection
  │       │       ├── Postgres writes row inside T1
  │       │       ├── COMMIT sent → T1 closes, data is permanent on disk
  │       │       └── connection is still held by the session
  │       │
  │       └── session.refresh(record)              ← SELECT to get auto-generated id
  │
  └── request ends — session.close()
          └── connection returned to pool

  ---
  The three layers together — your test fixture

  Now compare with what your fixtures do. The difference is intentional.

  # conftest.py:77-82
  async with db_engine.connect() as conn:   # borrow connection from pool
      await conn.begin()                    # open transaction T1 manually
      session = AsyncSession(bind=conn)     # session bound to conn — no new connection
      yield session
      await session.close()
      await conn.rollback()                 # rollback T1 — undo all test data

  The key difference: you open the transaction before giving the session to SQLAlchemy. SQLAlchemy sees the transaction is already open and will
  not send COMMIT when you call session.commit() inside the test. Instead it uses savepoints.

  test starts
  │
  ├── conn.begin() → T1 opens (outer transaction, owned by the fixture)
  │       │
  │       └── session bound to conn
  │
  ├── paris_query fixture
  │       │
  │       ├── session.add(WeatherQuery("Paris"))
  │       ├── session.commit()
  │       │       │
  │       │       ├── SQLAlchemy sees: conn already has T1
  │       │       ├── sends SAVEPOINT sp1 instead of BEGIN
  │       │       ├── flushes INSERT — row lands in T1 on the connection
  │       │       └── sends RELEASE SAVEPOINT sp1 (not COMMIT)
  │       │
  │       │       Postgres state:
  │       │       T1 (open): [ INSERT WeatherQuery("Paris") ]
  │       │                                ↑
  │       │                     visible to anyone using this same connection
  │       │
  │       └── session.refresh(record) → SELECT on same conn → sees the row ✓
  │
  ├── db_async_client injects the same session into the endpoint
  │       │
  │       ├── endpoint calls repo.get_cities_cloud(...)
  │       ├── SELECT runs on same conn, same T1 → finds Paris row ✓
  │       └── response has Paris ✓
  │
  └── fixture teardown
          ├── session.close()
          └── conn.rollback() → T1 rolled back
                                INSERT undone — Paris row gone
                                next test starts clean

  ---
  Why not just commit and delete after the test?

  You could. But the rollback approach is faster, cleaner, and safer:

  ┌────────────────────────────┬────────────────────────┬─────────────────────────────────────────────────┬─────────────────────────┐
  │          Approach          │         Speed          │                    Isolation                    │          Risk           │
  ├────────────────────────────┼────────────────────────┼─────────────────────────────────────────────────┼─────────────────────────┤
  │ Commit + DELETE after test │ slow (two round trips) │ poor (data leaks if test crashes)               │ test pollution if crash │
  ├────────────────────────────┼────────────────────────┼─────────────────────────────────────────────────┼─────────────────────────┤
  │ Rollback transaction       │ fast (one round trip)  │ perfect (T1 never visible to other connections) │ zero                    │
  └────────────────────────────┴────────────────────────┴─────────────────────────────────────────────────┴─────────────────────────┘

  The rollback approach also handles crashes gracefully — if your test process dies mid-test, Postgres automatically rolls back uncommitted
  transactions when the connection drops.

  ---
  One-line summary of each layer

  Connection  = the TCP pipe to Postgres. Carries SQL strings.
  Transaction = a "grouped work unit" inside a connection. COMMIT saves, ROLLBACK undoes.
  Session     = a Python object that translates ORM models into SQL and tracks their state.

  Session uses Connection.
  Transaction lives inside Connection.
  Session can borrow a Connection it doesn't own (bind=conn) — that's what your test does.