  ---                                                                                                                               
  Overview — the end-to-end flow          
                                                                                                                                    
  You type: /ticket CU-123                                                                                                          
           │                                                                                                                        
           ▼                                                                                                                        
  [MCP: ClickUp]  ←── fetches task description + acceptance-criteria checklist                                                      
           │                                                                                                                        
           ▼      
  [Skill: ticket-brief]  ←── structures raw ticket data into a dev brief                                                            
           │                                                                                                                        
           ▼
  [Agent: test-writer]  ←── reads brief + codebase, writes tests from AC (isolated)                                                 
           │                                                                                                                        
           ▼
  You review tests → approve → run pytest (tests FAIL — expected)                                                                   
           │                                                                                                                        
           ▼
  [Agent: implementor]  ←── reads failing tests + brief, implements feature                                                         
           │      
           ▼
  You run pytest (tests PASS)                                                                                                       
           │
           ▼                                                                                                                        
  [Skill: tdd-loop]  ←── validates cycle is complete, nothing skipped
           │                                                                                                                        
           ▼
  You type: /commit  ←── proposes commit message referencing ticket ID                                                              
           │                                                                                                                        
           ▼
  You type: /pr  ←── creates PR body from ticket description + AC checklist                                                         
           │                                                                                                                        
           ▼
  [Agent: pr-reviewer]  ←── reads diff + AC, returns structured review                                                              
                  
  ---
  Each piece, its type, and why
                                                                                                                                    
  MCP — ClickUp connection
                                                                                                                                    
  What it is: an external server that gives Claude native tools to call the ClickUp API (get_task, get_checklists, etc.) directly,  
  without you copy-pasting ticket content.                                                                                          
                                                                                                                                    
  Why MCP and not a command/skill: skills and commands only work with text you provide. MCP gives Claude live tool access to        
  external systems — it can fetch the ticket itself.
                                                                                                                                    
  Setup needed: configure the ClickUp MCP server in .mcp.json in the project root.                                                  
   
  ---                                                                                                                               
  Commands (3)    

  ┌──────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────┐
  │   Command    │                                           What it does                                            │
  ├──────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────┤              
  │ /ticket <id> │ Entry point: fetches ticket via MCP, invokes ticket-brief skill, then kicks off test-writer agent │
  ├──────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────┤              
  │ /commit      │ Proposes a commit message following project conventions, referencing the ClickUp ticket ID        │              
  ├──────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────┤              
  │ /pr          │ Creates a GitHub PR with body built from ticket description + AC checklist as a task list         │              
  └──────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────┘              
                  
  Why commands: all three are user-triggered, have a fixed structure, and need no autonomy — they're entry/exit points in the       
  workflow.       
                                                                                                                                    
  ---             
  Skills (3)
                                                                                                                                    
  ┌──────────────────┬────────────────────────────────────────────────────────────────────────┬─────────────────────────────────┐
  │      Skill       │                              What it does                              │   When Claude self-invokes it   │   
  ├──────────────────┼────────────────────────────────────────────────────────────────────────┼─────────────────────────────────┤
  │ ticket-brief     │ Transforms raw ClickUp data (description + AC items) into a structured │ Auto-invoked by /ticket command │
  │                  │  dev brief: context, constraints, list of testable requirements        │                                 │
  ├──────────────────┼────────────────────────────────────────────────────────────────────────┼─────────────────────────────────┤   
  │                  │ Enforces the TDD discipline: tests must exist and fail before          │ Auto-invoked whenever Claude is │
  │ tdd-loop         │ implementation starts; Claude cannot propose implementation without    │  about to write feature code    │   
  │                  │ prior test approval                                                    │                                 │   
  ├──────────────────┼────────────────────────────────────────────────────────────────────────┼─────────────────────────────────┤
  │ fastapi-patterns │ Project conventions: router → schema → service → repo layering,        │ Auto-invoked when adding a new  │   
  │                  │ dependency injection patterns, error handling rules                    │ endpoint or service             │   
  └──────────────────┴────────────────────────────────────────────────────────────────────────┴─────────────────────────────────┘
                                                                                                                                    
  Why skills: these are behavioral constraints on Claude within the current session. They don't need isolation — they need to see   
  the full conversation history (the brief, the tests, the discussion).
                                                                                                                                    
  ---             
  Agents (3)

  ┌─────────────┬───────────────────────────────────────────────────────────┬───────────────────────────────────────────────────┐
  │    Agent    │                       What it does                        │                   Why isolated                    │
  ├─────────────┼───────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┤
  │             │ Receives the dev brief, reads the existing test suite and │ Needs to scan the codebase fresh without          │
  │ test-writer │  schemas, writes a complete test file covering every AC   │ conversation noise; returns a focused test file   │
  │             │ item                                                      │                                                   │   
  ├─────────────┼───────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┤
  │             │ Receives the failing test file + dev brief, reads         │ Needs clean context focused on the task; avoids   │   
  │ implementor │ relevant source files, implements the feature to make     │ being influenced by earlier conversation tangents │
  │             │ tests pass                                                │                                                   │   
  ├─────────────┼───────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┤
  │ pr-reviewer │ Receives the git diff + AC checklist, checks each         │ Must be independent — a reviewer should not be    │
  │             │ criterion is covered, flags issues, rates confidence      │ the same "mind" that wrote the code               │   
  └─────────────┴───────────────────────────────────────────────────────────┴───────────────────────────────────────────────────┘
                                                                                                                                    
  Why agents: all three benefit from isolation. The test-writer shouldn't be distracted by implementation details discussed earlier.
   The reviewer must be fresh to be credible.
                                                                                                                                    
  ---             
  File structure

  .claude/
  ├── mcp.json                    ← ClickUp MCP server config
  ├── commands/
  │   ├── ticket.md               ← /ticket <id>
  │   ├── commit.md               ← /commit                                                                                         
  │   └── pr.md                   ← /pr
  ├── skills/                                                                                                                       
  │   ├── ticket-brief.md         ← parse ticket into dev brief                                                                     
  │   ├── tdd-loop.md             ← TDD discipline enforcer
  │   └── fastapi-patterns.md     ← project conventions                                                                             
  └── agents/     
      ├── test-writer.md          ← writes tests from AC                                                                            
      ├── implementor.md          ← implements from failing tests
      └── pr-reviewer.md          ← reviews PR against AC  