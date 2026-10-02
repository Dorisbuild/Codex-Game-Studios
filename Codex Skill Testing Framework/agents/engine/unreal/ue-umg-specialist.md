# Agent Test Spec: ue-umg-specialist

## Agent Summary
- **Domain**: UMG question hierarchy design, data binding patterns, CommonUI input routing and input action data, question styling (QuestionStyle assets), UI optimization (question pooling, ListView, invalidation)
- **Does NOT own**: UX flow and screen navigation design (ux-designer), gameplay logic (gameplay-programmer), backend data sources (game code), server communication
- **Gate IDs**: None; defers UX flow decisions to ux-designer

---

## Static Assertions (Structural)

- [ ] `description:` field is present and domain-specific (references UMG, question hierarchy, CommonUI)
- [ ] TOML `developer_instructions` names the permitted operations, subagent scope, and domain boundaries; execution permissions remain with the parent Codex session
- [ ] Shipped TOML omits model and reasoning overrides to inherit the parent session
- [ ] Agent definition does not claim authority over UX flow, navigation architecture, or gameplay data logic

---

## Test Cases

### Case 1: In-domain request — inventory question with data binding
**Input**: "Create an inventory question that shows a grid of item slots. Each slot should display item icon, quantity, and rarity color. It needs to update when the inventory changes."
**Expected behavior**:
- Produces a UMG question structure: a parent WBP_Inventory containing a UniformGridPanel or TileView, with a child WBP_InventorySlot question per item
- Describes data binding approach: either Event Dispatchers on an Inventory Component triggering a refresh, or a TileView fed UObject-based item data (not raw structs); it names the entry question's list-entry interface (`IUserObjectListEntry`) and marks it unverified against `docs/engine-reference/unreal/`, which does not document it
- Specifies how rarity color is driven: a QuestionStyle asset or a data table lookup, not hardcoded color values
- Output includes the question hierarchy, binding pattern, and the refresh trigger mechanism

### Case 2: Out-of-domain request — UX flow design
**Input**: "Design the full navigation flow for our inventory system — how the player opens it, transitions to character stats, and exits to the pause menu."
**Expected behavior**:
- Does not produce a navigation flow or screen transition architecture
- Names ux-designer, its coordination partner for interaction design, as the owner of the flow, and offers to build the screens on its layered architecture (Menu Layer, `UCommonActivatableQuestionStack`) once the flow is defined
- Does not make UX decisions (back button behavior, transition animations, modal vs. fullscreen) without a UX spec — it asks for the spec or lists these as open questions instead

### Case 3: Domain boundary — CommonUI input action mismatch
**Input**: "Our inventory question isn't responding to the controller Back button. We're using CommonUI."
**Expected behavior**:
- Identifies the likely causes: the question's Back binding does not point at the Back row of the project's `CommonInputActionDataBase` data table, or the question is not the activated, focused screen on its stack
- Explains the CommonUI input routing model: screens derive from `UCommonActivatableQuestion` and bind UI actions to data-table rows; only the focused, activated question consumes input and unfocused questions ignore it
- Provides the fix: verify the Back binding's data-table row and that the question is pushed onto (and active on) its activatable-question stack
- Distinguishes this from a hardware input binding issue (which would be Enhanced Input territory)

### Case 4: Question performance issue — many question instances per frame
**Input**: "Our leaderboard question creates 500 individual WBP_LeaderboardRow instances at once. The game hitches for 300ms when opening the leaderboard."
**Expected behavior**:
- Identifies the root cause: 500 question instantiations in a single frame causes a construction hitch
- Recommends switching to ListView or TileView with virtualization — only visible rows are constructed
- Explains the ListView data requirement: each row's data is a UObject-based entry item, not a raw struct; it names the row question's list-entry interface (`IUserObjectListEntry`) and marks it unverified against `docs/engine-reference/unreal/`
- If ListView is not appropriate, recommends pooling: pre-instantiate a fixed number of rows and recycle them with new data
- Output is a concrete recommendation with the specific UMG component to use, not a vague "optimize it"

### Case 5: Context pass — CommonUI setup already configured
**Input context**: Project uses CommonUI; its `CommonInputActionDataBase` data table defines these input action rows: Confirm, Back, Pause, Secondary.
**Input**: "Add a 'Sort Inventory' button to the inventory question that works with CommonUI."
**Expected behavior**:
- Uses the existing Secondary row (or recommends adding a new Sort row if Secondary is already allocated on this screen)
- Does NOT invent a new input action without noting that it must be added as a row to the project's CommonUI input action data table
- Uses a `UCommonButtonBase` for the button and CommonUI's input routing — not a non-CommonUI binding (e.g., raw key press in Event Graph or `APlayerController::InputComponent`)
- References the provided action rows explicitly in the recommendation

---

## Protocol Compliance

- [ ] Stays within declared domain (UMG structure, data binding, CommonUI, question performance)
- [ ] Redirects UX flow and navigation design requests to ux-designer, making no binding UX decisions itself
- [ ] Returns structured findings (question hierarchy + binding pattern) rather than freeform opinions
- [ ] Uses existing CommonUI input action rows from context; does not invent new ones without flagging that they must be added to the data table
- [ ] Recommends virtualized lists (ListView/TileView) before question pooling for large collections
- [ ] Asks "May I write this to [filepath]?" naming the file before writing

---

## Coverage Notes
- Case 3 (CommonUI input routing) requires project to have CommonUI configured; test is skipped if project does not use CommonUI
- Case 4 (performance) is a high-impact failure mode — 300ms hitches are shipping-blocking; prioritize this test case
- Case 5 is the most important context-awareness test for UI pipeline consistency
- No automated runner; review manually or via `$codex-skill-test`
