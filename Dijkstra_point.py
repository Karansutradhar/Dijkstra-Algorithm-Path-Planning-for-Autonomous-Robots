#!/usr/bin/env python
# coding: utf-8
'''

'''
import math
import numpy as np
import cv2
import time as t

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cost = math.inf
        self.parent = None

class Robot:
    def __init__(self, radius, clearance, start, goal):
        self.radius = radius
        self.clearance = clearance
        self.start = start
        self.goal = goal
        
def get_min_node(queue):
    min_node = 0
    for node in range(len(queue)):
        if queue[node].cost < queue[min_node].cost:
            min_node = node
    return queue.pop(min_node)

def node_exists(x,y, queue):
    for node in queue:
        if node.x == x and node.y == y:
            return queue.index(node)
        else:
            return None
        
def try_move(move, current_point, radius, clearance):
    if move == 'move_up':
        return move_up(current_point, radius, clearance)
    if move == 'move_down':
        return move_down(current_point, radius, clearance)
    if move == 'move_left':
        return move_left(current_point, radius, clearance)
    if move == 'move_right':
        return move_right(current_point, radius, clearance)
    if move == 'move_up_right':
        return move_up_right(current_point, radius, clearance)
    if move == 'move_up_left':
        return move_up_left(current_point, radius, clearance)
    if move == 'move_down_right':
        return move_down_right(current_point, radius, clearance)
    if move == 'move_down_left':
        return move_down_left(current_point, radius, clearance)

def ways_in(x,y): # a pixel with no obstacles or edges nearby can be achieved from 8 moves
    count = 0
    if y > 0: #from top
        count+=1
    if y < 200: #from bottom
        count+=1
    if x > 0: #from left
        count+=1
    if x < 200: #from right
        count+=1
    if x < 300 and y < 200: #bottom right
        count+=1
    if x < 300 and y > 0: #top left
        count+=1
    if x > 0 and y > 0: #top left
        count+=1
    if x > 0 and y < 200: #bottom right
        count+=1
    return count

def fill_pixel(img,x,y): #fill visited pixes
    img[y,x] = [255,0,0]
    return img

def backtrack(node): #create list of parent node locations
    parentList = list()
    parent = node.parent
    while parent is not None:
        parentList.append(parent)
        parent = parent.parent
    return parentList


def check_viableX(point):
    if point >= 0 and point < 300:
        return True
    else:
        print("Invalid")
        print()
        return False
    
def check_viableY(point):
    if point > 0 and point < 200:
        return True
    else:
        print("Invalid")
        print()
        return False

def check_oval(x,y):
    center = [150, 100]
    rx = 40 + radius+clearance
    ry = 20 + radius+clearance
    dist = (((x - center[0]) ** 2) / (rx ** 2)) + (((y - center[1]) ** 2) / (ry ** 2))
    if dist <= 1:
        print("Don't go in the oval!")
        return False
    else:
        return True
    
    
def check_circle(x,y):
    y = 200 - y
    center = [225, 150]
    dist = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
    
    if dist <= 25+radius+clearance:
        print("Don't go in the circle!")
        return False
    else:
        return True
    
def check_rectangle(x,y):
    y = 200-y
    one = [95,200-170]
    two = [30.5,200-132.5]
    three = [35.5,200-123.9]
    four = [100,200-161.4]
    
    m_bottom = (two[1]-one[1])/(two[0]-one[0])
    m_top = (three[1]-four[1])/(three[0]-four[0])
    m_right = (one[1]-four[1])/(one[0]-four[0])
    m_left = (two[1]-three[1])/(two[0]-three[0])
    
    #solve for y intercept  y=mx+b or b = y-mx
    b_bottom = one[1]-m_bottom*one[0]
    b_top = three[1]-m_top*three[0]
    b_left = two[1]-m_left*two[0]
    b_right = four[1]-m_right*four[0]
    
    # 0 = y -mx -b
    eq_top = y - m_top*x-(b_top+radius+clearance+1) #+1 for rounding error
    eq_bottom = y - m_bottom*x -(b_bottom-radius-clearance)
    eq_left = y -m_left*x-(b_left+radius+clearance+2) # +2 is from rounding
    eq_right = y - m_right*x -(b_right-radius-clearance)
    
    if eq_top <= 0 and eq_bottom >= 0 and eq_left <= 0 and eq_right >= 0:
        print("Don't go in the rectangle!")
        return False
    else:
        return True

def check_diamond(x,y):
    y = 200-y
    one = [225,200-190]
    two = [200,200-175]
    three = [225,200-160]
    four = [250,200-175]
    
    m_bottom = (two[1]-one[1])/(two[0]-one[0])
    m_top = (three[1]-four[1])/(three[0]-four[0])
    m_right = (one[1]-four[1])/(one[0]-four[0])
    m_left = (two[1]-three[1])/(two[0]-three[0])
    
    #solve for y intercept  y=mx+b or b = y-mx
    b_bottom = one[1]-m_bottom*one[0]
    b_top = three[1]-m_top*three[0]
    b_left = two[1]-m_left*two[0]
    b_right = four[1]-m_right*four[0]
    
    # 0 = y -mx -b
    eq_top = y - m_top*x-(b_top+radius+clearance)
    eq_bottom = y - m_bottom*x -(b_bottom-radius-clearance)
    eq_left = y -m_left*x-(b_left+radius+clearance)
    eq_right = y - m_right*x -(b_right-radius-clearance)
    
    if eq_top <= 0 and eq_bottom >= 0 and eq_left <= 0 and eq_right >= 0:
        print("Don't go in the diamond!")
        return False
    else:
        return True
    

def check_polygon(x,y):
    y = 200 - y
    one = [20,200-80]
    two = [25,200-15]
    three = [75,200-15]
    four = [100,200-50]
    five = [75,200-80]
    six = [50,200-50] 
    
    
    m_one = (one[1]-two[1])/(one[0]-two[0])
    m_two = (two[1]-three[1])/(two[0]-three[0])
    m_three = (three[1]-four[1])/(three[0]-four[0])
    m_four = (five[1]-four[1])/(five[0]-four[0])
    m_five = (six[1]-five[1])/(six[0]-five[0])
    m_six = (one[1]-six[1])/(one[0]-six[0])
    m_seven = (six[1]-three[1])/(six[0]-three[0])
    
    #solve for y intercept  y=mx+b or b = y-mx
    b_one = one[1]-m_one*one[0]
    b_two = two[1]-m_two*two[0]
    b_three = three[1]-m_three*three[0]
    b_four = four[1]-m_four*four[0]
    b_five = five[1]-m_five*five[0]
    b_six = six[1]-m_six*six[0]
    b_seven = six[1]-m_seven*six[0]
    
    # 0 = y -mx -b
    
    eq_one = y - m_one*(x+clearance+radius)-(b_one)
    eq_two = (y) - m_two*x -(b_two+clearance+radius) 
    eq_three = y -m_three*(x)-(b_three+clearance+radius)
    eq_four = y - m_four*x -(b_four-clearance-radius)
    eq_five = y - m_five*x - (b_five-clearance-radius)
    eq_six = y - (m_six*x) - (b_six-clearance-radius)
    eq_seven = y - m_seven*x-(b_seven) #interior line segment
    

    if eq_one <= 0 and eq_two <= 0 and eq_six>=0 and eq_seven >=0:
        print("Don't go in the polygon1!")
        return False
    
    if eq_three <= 0 and eq_four >= 0 and eq_five >= 0 and eq_seven <= 0:
        print("Don't go in the polygon2!")
        return False
    
    else:
        return True

def plot_workspace(x_start,y_start,x_goal,y_goal):
    img = 255 * np.ones((200, 300, 3), np.uint8)

    # Plot the diamond
    cords_square = np.array([[225 , 190 ],[200, 175 ], [225 , 160 ],[250 , 175]], dtype=np.int32)
    cv2.fillConvexPoly(img, cords_square, [0,0,0])
    
    # Plot the circle
    cv2.circle(img, (225, 50), 25, (0, 0, 0), -1)
    
    # Plot the oval
    cv2.ellipse(img, (150, 100), (40, 20), 0, 0, 360, 0, -1)
    
    # Plot the polygon
    poly1 = np.array([[20,80], [25,15],[75,15],[50,50]], dtype=np.int32)
    cv2.fillConvexPoly(img, poly1, [0,0,0])
    
    poly2 = np.array([[50,50], [75,15],[100,50],[75,80]], dtype=np.int32)
    cv2.fillConvexPoly(img, poly2, [0,0,0])
    
    # Plot rectangle
    poly3 = np.array([[95,170], [int(30.5),int(132.5)],[int(35.5),int(123.9)],[100,int(161.4)]], dtype=np.int32)
    cv2.fillConvexPoly(img, poly3, [0,0,0])

    return img

def move_up(point, radius, clearance):
    x = point[0]
    y = point[1]
    cost = 1
    if check_viableX(x) and check_viableY(y) and check_circle(x,y) and check_oval(x,y) and check_rectangle(x,y) and check_diamond(x,y)and check_polygon(x,y):
        new_point = [x, y - 1]
        return new_point, cost
    else:
        return None, None


def move_down(point, radius, clearance):
    x = point[0]
    y = point[1]
    cost = 1
    if check_viableX(x) and check_viableY(y) and check_circle(x,y) and check_oval(x,y) and check_rectangle(x,y)and check_diamond(x,y)and check_polygon(x,y):
        new_point = [x, y + 1]
        return new_point, cost
    else:
        return None, None


def move_left(point, radius, clearance):
    x = point[0]
    y = point[1]
    cost = 1
    if check_viableX(x) and check_viableY(y) and check_circle(x,y) and check_oval(x,y)and check_rectangle(x,y)and check_diamond(x,y)and check_polygon(x,y):
        new_point = [x - 1, y]
        return new_point, cost
    else:
        return None, None


def move_right(point, radius, clearance):
    x = point[0]
    y = point[1]
    cost = 1
    if check_viableX(x) and check_viableY(y) and check_circle(x,y) and check_oval(x,y)and check_rectangle(x,y)and check_diamond(x,y)and check_polygon(x,y):
        new_point = [x + 1, y]
        return new_point, cost
    else:
        return None, None


def move_up_right(point, radius, clearance):
    x = point[0]
    y = point[1]
    cost = np.sqrt(2)
    if check_viableX(x) and check_viableY(y) and check_circle(x,y) and check_oval(x,y)and check_rectangle(x,y)and check_diamond(x,y)and check_polygon(x,y):
        new_point = [x + 1, y - 1]
        return new_point, cost
    else:
        return None, None


def move_up_left(point, radius, clearance):
    x = point[0]
    y = point[1]
    cost = np.sqrt(2)
    if check_viableX(x) and check_viableY(y) and check_circle(x,y) and check_oval(x,y)and check_rectangle(x,y)and check_diamond(x,y)and check_polygon(x,y):
        new_point = [x - 1, y - 1]
        return new_point, cost
    else:
        return None, None


def move_down_right(point, radius, clearance):
    x = point[0]
    y = point[1]
    cost = np.sqrt(2)
    if check_viableX(x) and check_viableY(y) and check_circle(x,y) and check_oval(x,y)and check_rectangle(x,y)and check_diamond(x,y)and check_polygon(x,y):
        new_point = [x + 1, y + 1]
        return new_point, cost
    else:
        return None, None


def move_down_left(point, radius, clearance):
    x = point[0]
    y = point[1]
    cost = np.sqrt(2)
    if check_viableX(x) and check_viableY(y) and check_circle(x,y) and check_oval(x,y)and check_rectangle(x,y)and check_diamond(x,y) and check_polygon(x,y):
        new_point = [x - 1, y + 1]
        return new_point, cost
    else:
        return None, None


def djikstra(image, robot):
    
    radius = robot.radius
    clearance = robot.clearance
    
    start_node_pos = robot.start
    goal_node_pos = robot.goal
    
    image[start_node_pos[1], start_node_pos[0]] = [0, 255, 0]
    image[goal_node_pos[1], goal_node_pos[0]] = [0, 0, 255]
    
    start_node = Node(start_node_pos[0],start_node_pos[1])
    start_node.cost = 0

    waysIn = ways_in(goal_node_pos[0],goal_node_pos[1])
    print("Ways in", waysIn)
    
    visitedNodes = list()
    queue = [start_node]
    
    moves = ["move_up", "move_down", "move_left", "move_right",
               "move_up_right", "move_down_right", "move_up_left", "move_down_left"]
    counter = 0
    frame = 0
    
    while queue:
        current_node = get_min_node(queue)
        current_point = [current_node.x,current_node.y]
        visitedNodes.append(str(current_point))

        for move in moves:
            new_point, cost = try_move(move, current_point, radius, clearance)
            frame +=1
            if new_point is not None:
                if new_point == goal_node_pos:
                    
                    if counter < waysIn:
                        counter += 1
                        print("Goal reached " +str(counter) + " times")

                new_node = Node(new_point[0],new_point[1])
                new_node.parent = current_node

                image = fill_pixel(image, current_node.x,current_node.y)
                image[start_node_pos[1], start_node_pos[0]] = [0, 255, 0]
                image[goal_node_pos[1], goal_node_pos[0]] = [0, 0, 255]

                # update display every 75 nodes explored
                if frame % 75 == 0:
                    cv2.imshow("Map", image)
                    cv2.waitKey(1)
                
                if str(new_point) not in visitedNodes:
                    new_node.cost = cost + new_node.parent.cost
                    visitedNodes.append(str(new_point))
                    queue.append(new_node)
                else:
                    node_exist_index = node_exists(new_point[0],new_point[0], queue)
                    if node_exist_index is not None:
                        temp_node = queue[node_exist_index]
                        if temp_node.cost > cost + new_node.parent.cost:
                            temp_node.cost = cost + new_node.parent.cost
                            temp_node.parent = current_node
            else:
                continue
        if counter == waysIn:
            return new_node.parent, image
    return None, None

#################################################
start = False
goal = False

#change these values for point/rigid robot
radius = 0
clearance = 0


while start == False:
    x_start = input("Enter robot x position : ")
    x_start = int(x_start)
    y_start = input("Enter robot y position : ") 
    y_start = int(y_start)
    start = check_viableY(y_start)
    if start == True:
        start = check_viableX(x_start)
        if start ==True:
            start = check_oval(x_start,y_start)
            if start == True:
                start = check_circle(x_start,y_start)
                if start == True:
                    start = check_rectangle(x_start,y_start)
                    if start == True:
                        start = check_diamond(x_start,y_start)
                        if start == True:
                            start = check_polygon(x_start,200-y_start)
    
while goal == False:
    x_goal = input("Enter goal x position : ") 
    x_goal = int(x_goal)
    y_goal = input("Enter goal y position : ") 
    y_goal = int(y_goal)
    goal = check_viableY(y_goal)
    if goal == True:
        goal = check_viableX(x_goal)
        if goal ==True:
            goal = check_oval(x_goal,y_goal)
            if goal == True:
                goal = check_circle(x_goal,y_goal)
                if goal == True:
                    goal = check_rectangle(x_goal,y_goal)
                    if goal == True:
                        goal = check_diamond(x_goal,y_goal)
                        if goal == True:
                            goal = check_polygon(x_goal,200-y_goal)




start = t.time()
y_start = 200 - y_start
y_goal = 200 - y_goal

start_node = [x_start,y_start]
goal_node = [x_goal,y_goal]



robot1 = Robot(radius, clearance, start_node, goal_node)

workspace = plot_workspace(x_start,y_start,x_goal,y_goal)


solution, image = djikstra(workspace, robot1)
print("Time to solve: " + str(t.time()-start) + " seconds")
if solution is not None:
    parent_list = backtrack(solution)
    for parent in parent_list:
        x = parent.x
        y = parent.y
        image[y, x] = [0, 255, 0]
        cv2.imshow("Map", image)
        cv2.waitKey(25)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("No path to goal point")




