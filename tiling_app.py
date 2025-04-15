import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import io

# ========== 语言支持 ==========
lang = st.radio("语言 Language", ("中文", "English"), key="language_selector")

text = {
    "中文": {
        "title": "彩色 1x2 瓷砖铺满 n×n 格子",
        "intro": """
在一个 n×n 的格子中，使用自定义颜色的 1×2 瓷砖进行铺设，满足以下限制：

- 瓷砖可以水平或垂直放置；
- 同颜色同方向的瓷砖不能直接相邻；
- 你不必须使用所有颜色；
- 系统将返回合法拼法总数，并展示一种合法拼法的图形示例。
""",
        "grid_size": "输入网格大小 n（必须是偶数）",
        "color_count": "选择颜色种类数",
        "color_label": lambda i: f"选择第 {i+1} 种颜色",
        "button": "开始计算",
        "spinner": "正在搜索所有合法拼法，请稍候...",
        "result": lambda count: f"合法拼法总数为：`{count}`",
        "example": "以下是随机选择的一种合法拼法：",
        "explanation": "解题思路"
    },
    "English": {
        "title": "Tile an n×n Grid with 1×2 Colored Dominoes",
        "intro": """
Fill an n×n grid with 1×2 tiles using custom colors. The following rules apply:

- Tiles can be placed horizontally or vertically;
- Two tiles of the same color and direction cannot be adjacent;
- You are not required to use all colors;
- The app will show the total number of valid tilings and a sample layout.
""",
        "grid_size": "Grid size n (must be even)",
        "color_count": "Number of colors",
        "color_label": lambda i: f"Select Color #{i+1}",
        "button": "Start Calculation",
        "spinner": "Searching all valid tilings...",
        "result": lambda count: f"Total number of valid tilings: `{count}`",
        "example": "Here is one randomly selected valid tiling:",
        "explanation": "Solution Walkthrough"
    }
}

# ========== 页面标题与介绍 ==========
st.title(text[lang]["title"])
st.markdown(text[lang]["intro"])

# ========== 用户输入 ==========
n = st.number_input(text[lang]["grid_size"], min_value=2, max_value=8, step=2, value=4)
num_colors = st.slider(text[lang]["color_count"], min_value=2, max_value=5, step=1, value=2)

color_palette = []
for i in range(num_colors):
    default_color = "#FF0000" if i == 0 else "#0000FF" if i == 1 else f"#00{(i * 40) % 256:02X}FF"
    color_palette.append(st.color_picker(text[lang]["color_label"](i), default_color))

# ========== 基础逻辑 ==========
HORIZONTAL = 0
VERTICAL = 1
directions = [(0, 1), (1, 0)]
frames = []

def in_bounds(x, y, n):
    return 0 <= x < n and 0 <= y < n

def draw_grid(n, grid, color_palette):
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_aspect('equal')
    plt.gca().invert_yaxis()
    for x in range(n + 1):
        ax.axhline(x, color='gray', linewidth=0.5)
        ax.axvline(x, color='gray', linewidth=0.5)
    drawn = set()
    for i in range(n):
        for j in range(n):
            if (i, j) in drawn or grid[i][j] is None:
                continue
            color, direction = grid[i][j]
            dx, dy = directions[direction]
            x2, y2 = i + dx, j + dy
            rect = patches.Rectangle((j, i), dy + 1, dx + 1,
                                     linewidth=1,
                                     edgecolor='black',
                                     facecolor=color_palette[color % len(color_palette)],
                                     alpha=0.6)
            ax.add_patch(rect)
            drawn.add((i, j))
            drawn.add((x2, y2))
    buf = io.BytesIO()
    plt.axis('off')
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

def collect_with_animation(n, num_colors, sample_limit=10):
    results = []
    frames.clear()
    total_count = 0

    def dfs(x, y, grid):
        # 递归函数：尝试从 (x, y) 开始填砖，搜索所有合法铺法
        nonlocal total_count

        if x == n:
            # 终止条件：行号等于 n，说明整个棋盘填满，找到一个合法方案
            total_count += 1
            if len(results) < sample_limit:
                results.append([row.copy() for row in grid])
                if len(results) == 1:
                    frames.append(draw_grid(n, grid, color_palette))
            return

        if y == n:
            # 如果当前行填满，移动到下一行的第一个格子
            dfs(x + 1, 0, grid)
            return

        if grid[x][y] is not None:
            # 如果当前格子已经被填过，跳过它
            dfs(x, y + 1, grid)
            return

        for color in range(num_colors):
            # 尝试每一种颜色
            for direction, (dx, dy) in enumerate(directions):
                # 尝试横向或纵向放置
                x2, y2 = x + dx, y + dy
                # 计算另一端的位置
                if not in_bounds(x2, y2, n) or grid[x2][y2] is not None:
                    # 超出边界或目标格子已被占用则跳过
                    continue

                conflict = False
                # 检查是否与邻居发生颜色方向冲突
                for nx, ny in [(x - 1, y), (x, y - 1), (x2 + 1, y2), (x2, y2 + 1)]:
                    # 查看当前砖块四周是否有相同颜色和方向的砖块
                    if in_bounds(nx, ny, n) and grid[nx][ny] == (color, direction):
                        # 存在冲突，不能放置
                        conflict = True
                        break

                if conflict:
                    continue

                grid[x][y] = (color, direction)
                grid[x2][y2] = (color, direction)
                # 放置砖块到 grid 上
                if len(results) == 0:
                    frames.append(draw_grid(n, grid, color_palette))
                dfs(x, y + 1, grid)
                # 继续处理下一个格子
                grid[x][y] = None
                grid[x2][y2] = None
                # 回溯：移除刚才放置的砖块

    grid = [[None for _ in range(n)] for _ in range(n)]
    dfs(0, 0, grid)
    return results, total_count

# 👇 点击按钮后再显示结果和解释
if st.button(text[lang]["button"]):
    with st.spinner(text[lang]["spinner"]):
        all_tilings, total_count = collect_with_animation(n, num_colors)

    if all_tilings:
        chosen = random.choice(all_tilings)
        st.markdown(text[lang]["example"])
        st.image(draw_grid(n, chosen, color_palette), caption="示例")

    st.success(text[lang]["result"](total_count))

    if lang == "中文":
        st.markdown("""
### 解题思路与状态转移推导（中文）

我们从一个 2×2 的小格子开始分析所有合法铺法：

- 如果选择一个颜色，将其横放在 (0,0)-(0,1)，剩下的只能竖放在 (1,0)-(1,1)，否则会出现同方向同颜色冲突；
- 如果先选择竖放 (0,0)-(1,0)，则另一块需横放 (0,1)-(1,1)，同样避免同颜色同方向相邻。

这两种组合代表了铺法的最小状态单位（2×2）中可能的状态组合，揭示了状态间存在“颜色+方向”限制的依赖关系。

因此，我们不能使用简单的一维或二维 dp[x][y] 来建模，而需要考虑 `颜色+方向` 的状态组合。

我们在程序中采用显式记录状态的方法，即通过 `grid[x][y] = (color, direction)` 表示每一格的状态。

### 状态转移方程的推导：

我们以 DFS 的形式遍历整个 n×n 网格中的所有状态组合。对于每个空格 `(x,y)`：

1. 枚举颜色：`color ∈ [0, num_colors-1]`
2. 枚举方向：`direction ∈ {HORIZONTAL, VERTICAL}`
3. 计算其对应的第二格 `(x2, y2)`：
   ```python
   x2 = x + dx
   y2 = y + dy
   ```
4. 判断是否越界或已占用：
   ```python
   if not in_bounds(x2, y2, n) or grid[x2][y2] is not None:
       continue
   ```
5. 冲突检测：判断当前砖块周围是否已有相同 `(color, direction)` 的砖块：
   ```python
   for nx, ny in [(x-1,y), (x,y-1), (x2+1,y2), (x2,y2+1)]
   ```
6. 如果合法，则更新状态并进入下一格递归：
   ```python
   grid[x][y] = grid[x2][y2] = (color, direction)
   dfs(x, y+1)
   grid[x][y] = grid[x2][y2] = None  # 回溯
   ```

从动态规划角度来看，`dfs(x, y)` 可以视作状态转移函数：当前从 `(x,y)` 出发，尝试所有合法拼法路径。
每一个递归深度即代表“已放置砖块的数量”，通过剪枝可大幅减少冗余搜索路径。

最终，所有合法状态路径数量即为答案。

---

### 例子：图示 + 数学结合说明状态转移与 DFS 融合

我们以一个 2×2 的网格作为例子来可视化状态转移过程：

```
初始：
[ ][ ]
[ ][ ]
```

我们从 (0,0) 开始搜索：
1. 尝试放置一个横向红色瓷砖：
```
[R][R]
[ ][ ]
```
- 接下来必须放置竖向（颜色不同）的砖块在 (1,0)-(1,1)
- 成功构成一个合法拼法

2. 尝试放置一个纵向蓝色瓷砖：
```
[B][ ]
[B][ ]
```
- 接下来只能横向填充 (0,1)-(1,1)，如果颜色和方向不冲突，拼法合法

在这些过程中，我们实际形成了一个隐式的状态树：
每一个合法的 `(color, direction)` 放置构成一层节点，向下递归构成状态转移路径。

数学上我们可以将状态定义为：
- `S = (x, y, grid)`
- 状态转移：
```python
S' = (x, y+1, grid')  # 若成功放置砖块后进入下一个格子
```

DFS 实际上就是在构建一个状态转移图（树），其中剪枝条件限制了某些非法转移边。
我们不显式保存所有状态，而是通过递归函数隐式推进状态，同时在递归栈中完成回溯与撤销。

这种方式将“穷举 + 剪枝 + 转移”合并到 DFS 中，实现了结构化、可控的状态空间搜索。

---

### 为什么要使用 DFS 融合 DP？

传统的动态规划需要预先定义好所有的状态维度和转移方式，而本问题中状态组合非常复杂：不仅有位置 `(x, y)`，还有颜色、方向、邻接关系等限制，状态空间爆炸。

因此我们使用 DFS + 回溯的方式来**隐式枚举所有合法状态路径**，实现一种“按需展开”的动态规划。

程序中 `dfs(x, y, grid)` 的每一步逻辑如下：

1. **边界判断**：如果 `x == n`，说明整张网格已经铺满，找到一个合法方案，计数加一。
2. **换行推进**：如果当前列走到末尾，则换行递归处理下一行。
3. **已填跳过**：当前格子如果已有砖块覆盖，则跳过递归处理下一个格子。
4. **尝试所有颜色和方向**：枚举 `(color, direction)` 并尝试放置砖块，验证是否越界或被占。
5. **检查与相邻格冲突**：排除与相同颜色方向的邻格直接接壤的方案。
6. **放置砖块，递归继续**：如果合法，就将两格设为 `(color, direction)` 并递归进入下一个格子。
7. **回溯**：递归返回后清除刚刚放置的砖块，继续尝试其他放法。

这种方式结合了 DP 的状态转移思想与 DFS 的路径搜索能力，在无需显式构建庞大状态表的情况下完成高效搜索。
        """)
    else:
        st.markdown("""
### Solution Walkthrough (English)

We begin with a 2×2 grid to explore all valid placements:

- Placing a tile horizontally at (0,0)-(0,1) forces vertical at (1,0)-(1,1);
- Placing vertically at (0,0)-(1,0) forces horizontal at (0,1)-(1,1).

These configurations represent the minimal valid units, showing that legal transitions depend on **both color and direction**, not just position.

Thus, simple `dp[x][y]` is insufficient. Instead, we represent each cell state as a `(color, direction)` tuple via `grid[x][y] = (color, direction)`.

### Deriving State Transition Function:

Our program uses a DFS to simulate all possible domino placements on the board. For each empty cell `(x, y)`, we:

1. Enumerate colors: `color ∈ [0, num_colors-1]`
2. Enumerate directions: `direction ∈ {HORIZONTAL, VERTICAL}`
3. Compute the second cell `(x2, y2)` using:
   ```python
   x2 = x + dx
   y2 = y + dy
   ```
4. Validate boundary and occupation:
   ```python
   if not in_bounds(x2, y2, n) or grid[x2][y2] is not None:
       continue
   ```
5. Check adjacent conflicts:
   ```python
   for nx, ny in [(x-1,y), (x,y-1), (x2+1,y2), (x2,y2+1)]
   ```
   We reject placements where neighbors have the same color and direction.

6. If valid, place the domino and recurse:
   ```python
   grid[x][y] = grid[x2][y2] = (color, direction)
   dfs(x, y+1)
   grid[x][y] = grid[x2][y2] = None  # backtrack
   ```

This DFS acts as our implicit dynamic programming engine: `dfs(x, y)` encodes all ways to tile from `(x, y)` onward.
Each recursive call corresponds to a transition in the state space, and backtracking prunes invalid branches.

Finally, the total count of valid paths found equals the number of legal tilings.

---

### Example: Visualizing State Transition + DFS Fusion

Take a 2×2 grid as a minimal case:
```
Initial:
[ ][ ]
[ ][ ]
```

Starting from (0,0):
1. Try placing a horizontal red tile:
```
[R][R]
[ ][ ]
```
- Now must place a vertical tile at (1,0)-(1,1) with a different color to satisfy constraints
- This forms a valid solution path

2. Try placing a vertical blue tile:
```
[B][ ]
[B][ ]
```
- Then horizontally fill (0,1)-(1,1) if color/direction is valid

Each placement forms a node in an implicit state tree, with `(color, direction)` as the branching factor.

We define state as:
- `S = (x, y, grid)`
- Transition:
```python
S' = (x, y+1, grid')
```

DFS builds this state-space tree without storing all paths explicitly.
Pruning invalid placements is equivalent to removing illegal transition edges.

Thus, DFS + backtracking becomes a structured and implicit dynamic programming method over the state space.

---

### Why do we embed DFS into DP logic?

Traditional DP relies on clearly defined state dimensions and transition rules. However, this tiling problem involves a **combinatorially complex** state: position `(x, y)`, color, direction, and neighbor constraints — making explicit DP tables infeasible.

We use DFS + backtracking as a way to **implicitly enumerate valid state transitions** in a dynamic-programming-like manner.

In the code, each `dfs(x, y, grid)` call performs the following steps:

1. **Termination condition**: When `x == n`, all cells are filled — a valid solution is found and counted.
2. **Row shift**: If `y == n`, we move to the next row.
3. **Skip filled**: If the current cell is already filled, recurse to the next cell.
4. **Try all color and direction pairs**: For each `(color, direction)`, compute the second cell, and skip if it's invalid.
5. **Conflict detection**: We reject the placement if it violates adjacency constraints.
6. **Recursive placement**: Temporarily mark the grid, recurse into the next cell.
7. **Backtrack**: Clear the placement after returning to try other combinations.

This blends DFS recursion with the essence of DP transitions — exploring all valid paths without constructing an explicit DP table, making it both flexible and efficient.
        """)

    # 以下为伪代码结构补充和进一步解释：
    if lang == "中文":
        st.code("""
# DFS 主体伪代码结构
if x == n:
    return 1

if y == n:
    return dfs(x + 1, 0, grid)

if grid[x][y] is not None:
    return dfs(x, y + 1, grid)

total = 0
for color in range(num_colors):
    for direction in [HORIZONTAL, VERTICAL]:
        dx, dy = directions[direction]
        x2, y2 = x + dx, y + dy

        if not in_bounds(x2, y2, n) or grid[x2][y2] is not None:
            continue

        conflict = False
        for nx, ny in [(x - 1, y), (x, y - 1), (x2 + 1, y2), (x2, y2 + 1)]:
            if in_bounds(nx, ny, n) and grid[nx][ny] == (color, direction):
                conflict = True
                break
        if conflict:
            continue

        grid[x][y] = (color, direction)
        grid[x2][y2] = (color, direction)
        total += dfs(x, y + 1, grid)
        grid[x][y] = None
        grid[x2][y2] = None

return total
""")
        st.markdown("""
### 状态转移的思维提升
- 尽管我们没有显式写出三维 `dp[x][y][状态]`，但实际每一个 `grid[x][y]` 的内容就是一个隐式状态记录。
- 使用 DFS 递归推进，就相当于遍历整个状态图。
- 每一个递归深度即表示铺砖的进展，冲突剪枝就相当于剪去非法转移。
""")
    else:
        st.code("""
def dfs(x, y, grid):
    if x == n:
        return 1

    if y == n:
        return dfs(x + 1, 0, grid)

    if grid[x][y] is not None:
        return dfs(x, y + 1, grid)

    total = 0
    for color in range(num_colors):
        for direction in [HORIZONTAL, VERTICAL]:
            dx, dy = directions[direction]
            x2, y2 = x + dx, y + dy

            if not in_bounds(x2, y2, n) or grid[x2][y2] is not None:
                continue

            conflict = False
            for nx, ny in [(x - 1, y), (x, y - 1), (x2 + 1, y2), (x2, y2 + 1)]:
                if in_bounds(nx, ny, n) and grid[nx][ny] == (color, direction):
                    conflict = True
                    break
            if conflict:
                continue

            grid[x][y] = (color, direction)
            grid[x2][y2] = (color, direction)
            total += dfs(x, y + 1, grid)
            grid[x][y] = None
            grid[x2][y2] = None

    return total
""")
        st.markdown("""
### DFS as Implicit DP
- Though we don’t use an explicit `dp[x][y][state]`, the `grid[x][y]` tuple implicitly encodes the state.
- Each recursive DFS call represents a transition step in this DP space.
- The depth of the recursion equals the number of dominoes placed, and pruning eliminates invalid paths.
""")
