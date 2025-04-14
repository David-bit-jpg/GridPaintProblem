import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

# ========== 页面标题与介绍 ==========
st.title("🧱 彩色 1x2 瓷砖铺满 n×n 格子")
st.markdown("""
在一个 n×n 的格子中，使用自定义颜色的 1×2 瓷砖进行铺设，满足以下限制：

- 瓷砖可以水平或垂直放置；
- 同颜色同方向的瓷砖**不能直接相邻**；
- 你不必须使用所有颜色；
- 系统将返回合法拼法总数，并展示一种合法拼法的图形示例。
""")

# ========== 用户输入部分 ==========
n = st.number_input("输入网格大小 n（必须是偶数）", min_value=2, max_value=8, step=2, value=4)
num_colors = st.slider("选择颜色种类数", min_value=2, max_value=5, step=1, value=2)

# 初始化颜色选择器，确保合法 HEX 值
color_palette = [
    st.color_picker("选择第一种颜色", "#FF0000"),
    st.color_picker("选择第二种颜色", "#0000FF")
]
for i in range(2, num_colors):
    hex_part = f"{(i * 40) % 256:02X}"
    default_color = f"#00{hex_part}FF"
    color_palette.append(st.color_picker(f"选择第 {i+1} 种颜色", default_color))

# ========== 常量与函数 ==========
HORIZONTAL = 0
VERTICAL = 1
directions = [(0, 1), (1, 0)]  # 横向 / 纵向

def in_bounds(x, y, n):
    return 0 <= x < n and 0 <= y < n

# ========== 可视化 ==========
def draw_tiling(n, grid, color_palette):
    fig, ax = plt.subplots(figsize=(6, 6))
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
    st.pyplot(fig)

# ========== 收集所有拼法 ==========
def collect_all_tilings(n, num_colors, max_samples=1000):
    results = []
    def dfs(x, y, grid):
        if len(results) >= max_samples:
            return

        if x == n:
            results.append([row.copy() for row in grid])
            return

        if y == n:
            dfs(x + 1, 0, grid)
            return

        if grid[x][y] is not None:
            dfs(x, y + 1, grid)
            return

        for color in range(num_colors):
            for direction, (dx, dy) in enumerate(directions):
                x2, y2 = x + dx, y + dy
                if not in_bounds(x2, y2, n) or grid[x2][y2] is not None:
                    continue

                # 相邻限制判断
                conflict = False
                for nx, ny in [(x - 1, y), (x, y - 1), (x2 + 1, y2), (x2, y2 + 1)]:
                    if in_bounds(nx, ny, n) and grid[nx][ny] == (color, direction):
                        conflict = True
                        break
                if conflict:
                    continue

                # 放置
                grid[x][y] = (color, direction)
                grid[x2][y2] = (color, direction)
                dfs(x, y + 1, grid)
                grid[x][y] = None
                grid[x2][y2] = None

    grid = [[None for _ in range(n)] for _ in range(n)]
    dfs(0, 0, grid)
    return results

# ========== 执行与展示 ==========
if st.button("开始计算"):
    with st.spinner("正在搜索所有合法拼法，请稍候..."):
        all_tilings = collect_all_tilings(n, num_colors, max_samples=1000)

    st.success(f"🎉 合法拼法总数为：`{len(all_tilings)}`")

    if all_tilings:
        chosen = random.choice(all_tilings)
        st.markdown("以下是随机选择的一种合法拼法：")
        draw_tiling(n, chosen, color_palette)
