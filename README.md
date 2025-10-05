# LangGraph 101 Course & Projects
## TL;DR
LangGraph is a Python framework for designing and managing the flow of tasks in your application using graph structures. Bassicly, langgraph used for multi-agent to make that interactively with graph.

## Core Concepts
### Type Annotations
***
#### 1. TypedDict
**What is it?**
  It's a way to tell Python that a regular dictionary should have specific keys with specific types for their values.
**Example:**
  ```python
  from typing import TypedDict
  class Movie(TypedDict):
      name: str
      year: int
  # Now Movie must have 'name' (string) and 'year' (int)
  my_movie = Movie(name='Avengers', year=2019)
  ```
**Why use it?**
  Safer code, Python and your code editor can catch bugs if you try the wrong type.
***
#### 2. Union
**What is it?**
  It means a value can be *one of several* types.
**Example:**
  ```python
  from typing import Union
  def square(x: Union[int, float]):
      return x * x
  ```
**Why use it?**
  Flexibility: The function works with different (but specific) types.

***
#### 3. Optional
**What is it?**
  It says a variable can have a value *or* be `None` (empty).
  **Example:**
  ```python
  from typing import Optional
  def greet(name: Optional[str]):
      if name is not None:
          print(f'Hi, {name}')
      else:
          print('Hi, random person')
  ```
**Why use it?**
  Use for things that might be missing or unset.

***
#### 4. Any
**What is it?**
  It means "literally *any* type." Use cautiously.
**Example:**
  ```python
  from typing import Any
  def print_value(x: Any):
      print(x)
  ```
**Why use it?**
  Maximum flexibility; least safety. Only use if you must!

***
#### 5. Lambda
**What is it?**
  It's a *mini function* you write fast, often for tiny one-off tasks.
**Example:**
  ```python
  square = lambda x: x * x
  print(square(5))  # 25
  nums = [1,2,3,4]
  squares = list(map(lambda x: x*x, nums))  # [1,4,9,16]
  ```
**Why use it?**
  Short, simple functions written inline.

***
#### 6. Annotated
**What is it?**
  Lets you attach extra info (like constraints or metadata) to a type hint.
**Example:**
  ```python
  from typing import Annotated
  PositiveInt = Annotated[int, "Must be positive"]
  def set_age(age: PositiveInt):
      pass
  ```
**Why use it?**
  Useful for frameworks or validation, lets you give context beyond just the basic type.

***
#### **7. Sequence**
**What is it?**
  Stands for any **ordered collection** (like `list`, `tuple`) that you can index and loop through.
**Example:**
  ```python
  from typing import Sequence
  def total(items: Sequence[int]) -> int:
      return sum(items)
  # Works for both [1,2,3] and (1,2,3)
  ```
**Why use it?**
  Accepts both lists and tuples (but not sets or dicts).

***

### LangGraph Elements
***
#### 1. States
- Think of *state* as the app’s memory or a shared whiteboard everyone writes on.
- It holds current info (variables, data) nodes can read or change.
- Like notes on a whiteboard updated as the meeting progresses.

#### 2. Nodes
- Nodes are individual tasks or functions.
- Each node does one job: gets the current state, processes it, returns updated data.
- Imagine stations on an assembly line, each performing one step.

#### 3. Graphs
- The whole workflow connecting nodes together.
- Like a roadmap showing paths from city to city (nodes) with choices on routes.
- It shows the sequence and logic flow.

#### 4. Edges
- Edges connect nodes, showing the order to run tasks.
- Like train tracks between stations guiding where the train (state) moves next.

#### 5. Conditional Edges
- Special edges that decide next node based on a condition.
- Like traffic lights: green means go one way, red another (if-else logic).

#### 6. Start/End Points
- Start point: a virtual node marking where the graph begins (no action itself).
- End point: where execution finishes.
- Think of it as the front door (start) and exit (end) of the workflow.

#### 7. Tools
- Helpers or external capabilities the agent can use.
- For example, APIs, calculators, databases.

#### 8. Tool Nodes
- Nodes that call these tools.
- Like a station that uses a special machine from the toolbox.

#### 9. State Graphs
- An advanced graph managing the overall app state and how nodes interact with it.

#### 10. Message Types
- Different roles of messages exchanged during conversation or processing:
  - **Human:** user messages
  - **AI:** responses from the language model
  - **System:** instructions or settings
  - **Tool:** output from tools
  - **Function:** messages triggered by functions/code

***
[LangGraph Complete Course for Beginners – Complex AI Agents with Python](https://www.youtube.com/watch?v=jGg_1h0qzaM)
