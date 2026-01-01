import cv2
import matplotlib.pyplot as plt
import numpy as np
import easyocr

reader = easyocr.Reader(['en'], gpu=False)

def printGrid(grid):
    sep = "    "
    n = len(grid)

    print("_"*41)
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 0:
                print(".", end=sep)
            else:
                print(grid[i][j], end=sep)
        print()
        print("-"*41)

def hasDuplicates(grid, row_start, row_end, col_start, col_end):
    
    res = []
    for row in range(row_start, row_end+1):
        for col in range(col_start, col_end+1):
            res.append(grid[row][col])

    m = {}
    for elem in res:
        if elem == 0:
            continue
        if elem in m:
            m[elem] += 1
        else:
            m[elem] = 1

    for key in m:
        if m[key] > 1:
            return True
    
    
    return False

def isCorrect(grid):
    n = len(grid)
    
    for x in range(n):
        if hasDuplicates(grid, x, x, 0, 8):
            return False
        if hasDuplicates(grid, 0, 8, x, x):
            return False
    
    ends = [-1, 2, 5, 8]

    for i in range(1, 4):
        for j in range(1, 4):
            if hasDuplicates(grid, ends[i-1]+1, ends[i], ends[j-1]+1, ends[j]):
                return False
    
    return True

def solve(grid, unsolved_indices, idx):

    if idx == len(unsolved_indices):
        return True
    
    [x, y] = unsolved_indices[idx]        

    for val in range(1, 10):
        grid[x][y] = val
        isC = isCorrect(grid)
        if isC and solve(grid, unsolved_indices, idx+1):
            return True

    grid[x][y] = 0
    
    return False

def solvePuzzle(grid):
    unsolved_indices = []

    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                unsolved_indices.append([i,j])

    solve(grid, unsolved_indices, 0) # 3195

    return grid

def is_blank(image):
    mean, std_dev = cv2.meanStdDev(image)
    if np.all(std_dev < 10): 
        return True
    return False

def read_number(image):

    if is_blank(image):
        return 0

    results = reader.readtext(
        image,
        allowlist='123456789',
        detail=0
    )

    if not results:
        return 7

    # If multiple detections, join or pick largest later
    return "".join(results)

def get_grid():
    image = cv2.imread("image.png")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, image = cv2.threshold(image,200,255,cv2.THRESH_BINARY)
    kernel = np.ones((7,7),np.uint8)
    image = cv2.erode(image, kernel,iterations = 1)

    contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    big_box_contour = contours[1]
    big_box_area = cv2.contourArea(big_box_contour)
    small_sq_area_approx = big_box_area / 100

    big_x, big_y, _, _ = cv2.boundingRect(big_box_contour)

    coordinates = []

    for c in range(2, len(contours)):
        area = cv2.contourArea(contours[c])

        if ((0.8*small_sq_area_approx) < area) and (area < (1.2*small_sq_area_approx)):
            x,y,w,h = cv2.boundingRect(contours[c])
            coordinates.append([x,y,w,h])

    sudoku = [[0]*9 for _ in range(9)]

    for coor in coordinates:
        [x,y,w,h] = coor

        dy = min(int((y - big_y) / h), 8)
        dx = min(int((x - big_x) / w), 8)

        sudoku[dy][dx] = image[y:y+h, x:x+w]
    
    sudoku_digits = [[0]*9 for _ in range(9)]

    for i in range(9):
        for j in range(9):
            pred = read_number(sudoku[i][j])
            sudoku_digits[i][j] = int(pred)
    
    return sudoku_digits

unsolvedSudoku = get_grid()

print("Unsolved: ")
printGrid(unsolvedSudoku)

print(
    "Is this your puzzle?" \
    "\nIf not, please input corrections in the format: row column correct_value (1-indexed)." \
    "\nElse, press Enter."
)

while True:
    inp = input()

    if inp == "": break

    [x,y,val] = inp.split(" ")
    unsolvedSudoku[int(x)-1][int(y)-1] = int(val)

    printGrid(unsolvedSudoku)

print("Solved: ") 
printGrid(solvePuzzle(unsolvedSudoku))
