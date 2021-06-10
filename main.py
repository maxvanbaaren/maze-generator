import random
from tkinter import *
from collections import deque


def make_maze(m, n):  # m rows, n columns

    nodes = []  # list of all nodes

    for i in range(1, m + 1):  # creates all maze nodes
        for j in range(1, n + 1):
            nodes.append((i, j))

    edges = []  # list of all edges

    for i in nodes:  # assigns weights to all edges
        if i[0] < m:
            weight = random.randint(1, 10)
            edges.append(((i[0], i[1]), (i[0] + 1, i[1]), weight))
        if i[1] < n:
            weight = random.randint(1, 10)
            edges.append(((i[0], i[1]), (i[0], i[1] + 1), weight))

    sort_weights(edges)
    mst = make_mst(nodes, edges)
    walls = make_walls(m, n, nodes, edges, mst)
    search = dfs(m, n, walls)
    solution = search[0]
    steps = search[1]

    solution_set = set()
    for i in solution:
        solution_set.add(i)

    make_solution_file(m, n, steps)

    draw_maze(m, n, nodes, walls, solution_set)


def sort_weights(edges):  # merge sorts list of edges by weight

    if len(edges) > 1:
        m = len(edges) // 2
        left = edges[:m]
        right = edges[m:]
        sort_weights(left)
        sort_weights(right)
        i = j = k = 0

        while i < len(left) and j < len(right):
            if left[i][2] < right[j][2]:
                edges[k] = left[i]
                i += 1
            else:
                edges[k] = right[j]
                j += 1
            k += 1

        while i < len(left):
            edges[k] = left[i]
            i += 1
            k += 1

        while j < len(right):
            edges[k] = right[j]
            j += 1
            k += 1


def make_mst(nodes, edges):  # constructs minimum spanning tree

    parent = {}
    rank = {}
    mst = set()  # set representing minimum spanning tree

    def find_node(node):  # finds root for node
        if parent[node] != node:
            parent[node] = find_node(parent[node])
        return parent[node]

    def union(node1, node2):  # combines sets if roots differ
        root1 = find_node(node1)
        root2 = find_node(node2)
        if root1 != root2:
            if rank[root1] > rank[root2]:
                parent[root1] = root2
            else:
                parent[root1] = root2
            if rank[root1] == rank[root2]:
                rank[root2] += 1

    for i in nodes:  # sets all roots of nodes to themselves and all ranks to 0
        parent[i] = i
        rank[i] = 0

    for i in edges:  # traverses list of edges, combining sets if needed
        if find_node(i[0]) != find_node(i[1]):
            union(i[0], i[1])
            mst.add(i)  # add safe edge to mst

    return mst


def make_walls(m, n, nodes, edges, mst):  # assigns each node with a list of 4 values representing surrounding walls

    walls = {}  # set connecting nodes to wall info

    for i in nodes:  # if unchanged, nodes have walls in all directions
        walls[i] = [1, 1, 1, 1]

    for i in edges:  # sets locations without walls
        if i in mst:
            if i[0][0] < i[1][0]:
                walls[i[0]][2] = 0
                walls[i[1]][0] = 0
            if i[0][1] < i[1][1]:
                walls[i[0]][1] = 0
                walls[i[1]][3] = 0

    walls[(1, 1)][3] = 0  # left opening in (1, 1)
    walls[(m, n)][1] = 0  # right opening in (m, n)

    return walls


def dfs(m, n, walls):  # uses depth-first search to solve maze

    stack = deque()  # current path
    steps = []  # list of all steps taken
    visited = set()  # set of all visited nodes
    current = (1, 1)  # current node
    finish = (m, n)  # maze exit

    while True:

        stack.append(current)  # add current node to current path
        steps.append(current)  # add current node to list of steps

        if current == finish:  # check if at exit
            return [stack, steps]

        if current not in visited:  # add unvisited node to visited
            visited.add(current)

        if walls[current][1] == 0 and (current[0], current[1] + 1) not in visited:  # if no wall to right and node to
            # right not visited
            current = (current[0], current[1] + 1)  # move one node to right
        elif walls[current][2] == 0 and (current[0] + 1, current[1]) not in visited:  # if no wall below and node
            # below not visited
            current = (current[0] + 1, current[1])  # move one node down
        elif walls[current][3] == 0 and (current[0], current[1] - 1) not in visited:  # if no wall to left and node
            # to left not visited
            current = (current[0], current[1] - 1)  # move one node to left
        elif walls[current][0] == 0 and (current[0] - 1, current[1]) not in visited:  # if no wall above and node
            # above not visited
            current = (current[0] - 1, current[1])  # move one node up
        else:  # if no valid moves
            stack.pop()  # remove current node from current path
            current = stack.pop()  # backtrack


def make_solution_file(m, n, steps):  # writes file containing string representation of the maze solution, including
    # total number of steps needed to solve maze

    solution_file = open('solution.txt', 'w')
    print(str(m) + ' ' + str(n) + ' ' + str(len(steps)), file=solution_file)
    for i in steps:
        print(str(i[0]) + ' ' + str(i[1]), file=solution_file)
    solution_file.close()


def draw_maze(m, n, nodes, walls, solution_set):  # draws the maze and maze solution

    window = Tk()
    window.title('Maze')
    window2 = Tk()
    window2.title('Maze Solution')

    if m >= n:
        size = m / 5
    else:
        size = n / 5
    size = 100 / size
    border = size / 2

    canvas = Canvas(window, width=size * n, height=size * m)
    canvas2 = Canvas(window2, width=size * n, height=size * m)

    for i in nodes:

        #  calculate locations of node sides
        top = border + (i[0] - 1) * ((size * m - 2 * border) / m)
        bottom = border + i[0] * ((size * m - 2 * border) / m)
        left = border + (i[1] - 1) * ((size * n - 2 * border) / n)
        right = border + i[1] * ((size * n - 2 * border) / n)

        if i in solution_set:  # checks if node is apart of solution path
            canvas2.create_rectangle(left, top, right, bottom,
                                     fill='spring green', outline='spring green')  # fill in nodes that are in mst

        if walls[i][0] == 1:  # draw wall on top
            canvas.create_line(left, top, right, top)
            canvas2.create_line(left, top, right, top)
        if walls[i][1] == 1:  # draw wall on right
            canvas.create_line(right, top, right, bottom)
            canvas2.create_line(right, top, right, bottom)
        if walls[i][2] == 1:  # draw wall on bottom
            canvas.create_line(left, bottom, right, bottom)
            canvas2.create_line(left, bottom, right, bottom)
        if walls[i][3] == 1:  # draw wall on left
            canvas.create_line(left, top, left, bottom)
            canvas2.create_line(left, top, left, bottom)

    canvas.pack()
    canvas2.pack()
    window.mainloop()
    window2.mainloop()


make_maze(50, 50)  # create maze for given m and n
