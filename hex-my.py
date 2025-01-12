# all math is explain in https://www.redblobgames.com/grids/hexagons/

from raylib import *
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum

SCREEN_WIDTH = 1198
SCREEN_HEIGHT = 798
                
@dataclass
class PositionRect:
    x: int
    y: int
    w: int
    h: int
    
    def size(self):
        return self.h, self.w

@dataclass
class Monster:
    texture: any
    position: Tuple[int, int]
    name: str

class GridType(Enum):
    POINTY_TOP_EVEN_R = 1 #H3 combat type
    POINTY_TOP_ODD_R = 2
    FLAT_TOP_EVEN_Q = 3
    FLAT_TOP_ODD_Q = 4


@dataclass
class HexCell:
    row: int 
    col: int
    cx: int
    cy: int
    grid_type: GridType 
    radius: int 
    points: List[int] = field(init=False) 
    passable: bool = True
    monster: Optional[Monster] = None 

    def __post_init__(self):
        self.points = self._get_hex_vertices()

    def _get_hex_vertices(self):
        angle_deg = lambda i: 60  * i - (30 if self.grid_type in (GridType.POINTY_TOP_EVEN_R, GridType.POINTY_TOP_ODD_R) else 0)
        angle_rad = lambda i: math.pi / 180 * angle_deg(i)
        poin = lambda i: (self.cx + self.radius * math.cos(angle_rad(i)), self.cy + self.radius * math.sin(angle_rad(i)))
        return [poin(i) for i in range(6)] 
        

class HexGrid:
    def __init__(self, rows: int, cols: int, dest_rect: PositionRect, grid_type: GridType):
        self.dest_rect = dest_rect 
        self.rows = rows 
        self.cols = cols 
        self.grid_type = grid_type

        self.radius, self.offset_x, self.offset_y = self._calculate_hex_radius_and_xy_offsets()
        self.hexs = [[HexCell(r, c, *self.get_hex_center(r, c), grid_type, self.radius) for c in range(self.cols)] for r in range(self.rows)]
        self.hovered_hex_coords = None 


    def _get_hex_geomatry(self):
        """Instance method to get hex geometry values for this grid"""
        return HexGrid.get_hex_geometry_for_type(self.grid_type)
     
    @staticmethod
    def get_hex_geometry_for_type(grid_type: GridType):
        """Static method to get hex geometry values for a specific grid type"""
        match grid_type:
            case GridType.POINTY_TOP_EVEN_R | GridType.POINTY_TOP_ODD_R:
                hex_height = 2
                hex_width = math.sqrt(3)
                vertical_spacing = 3/4 * hex_height
                horizontal_spacing = hex_width

            case GridType.FLAT_TOP_EVEN_Q | GridType.FLAT_TOP_ODD_Q:
                hex_width = 2
                hex_height = math.sqrt(3)
                horizontal_spacing = 3/4 * hex_width
                vertical_spacing = hex_height

        return hex_width, hex_height, horizontal_spacing, vertical_spacing
   

    @staticmethod
    def _calc_2d_distance(p1x, p1y, p2x, p2y):
        return math.sqrt((p2x - p1x)**2 + (p2y - p1y)**2)
   

    def _point_to_hex(self, px, py):
        for r, row in enumerate(self.hexs):
            for c, cell in enumerate(row):
                if CheckCollisionPointPoly((px, py), cell.points, 6):
                    return cell.row, cell.col


    @staticmethod
    def calculate_rect_size(radius: float, grid_type: GridType, rows: int, cols: int):
        """
        Calculate the minimum rectangle size needed to fit a hex grid with given parameters.
        Returns calculated w,h
        """
        hex_width, hex_height, horizontal_spacing, vertical_spacing = HexGrid.get_hex_geometry_for_type(grid_type)
        match grid_type:
            case GridType.POINTY_TOP_EVEN_R | GridType.POINTY_TOP_ODD_R:
                if rows == 1:
                    total_width = radius * hex_width * cols
                else:
                    total_width = radius * hex_width * (cols + 0.5)
                total_height = radius * (hex_height + vertical_spacing * (rows - 1))
                
            case GridType.FLAT_TOP_EVEN_Q | GridType.FLAT_TOP_ODD_Q:
                total_width = radius * (hex_width + horizontal_spacing * (cols - 1))
                total_height = radius * hex_height * (rows + 0.5)
        
        return int(total_width), int(total_height)


    def _calculate_hex_radius_and_xy_offsets(self):
        target_height, target_width = self.dest_rect.size()
        hex_width, hex_height, horizontal_spacing, vertical_spacing = self._get_hex_geomatry()
        
        match self.grid_type:
            case GridType.POINTY_TOP_EVEN_R:
                if self.rows == 1:
                    w_radius = target_width / (self.cols * hex_width)
                    h_radius = target_height / hex_height
                elif self.cols == 1:
                    w_radius = target_width / (1.5 * hex_width)
                    h_radius = target_height / ((self.rows - 1) * vertical_spacing + hex_height)
                else:
                    w_radius = target_width / ((self.cols + 0.5) * hex_width)
                    h_radius = target_height / ((self.rows - 1) * vertical_spacing + hex_height)

                radius = min(w_radius, h_radius)
                total_width = radius * hex_width * (self.cols if self.rows == 1 else self.cols + 0.5)
                total_height = radius * (hex_height + vertical_spacing * (self.rows - 1))

            case GridType.POINTY_TOP_ODD_R:
                w_radius = target_width / ((self.cols + 0.5) * hex_width)
                h_radius = target_height / ((self.rows - 1) * vertical_spacing + hex_height)

                radius = min(w_radius, h_radius)
                total_width = radius * hex_width * (self.cols + 0.5)
                total_height = radius * (hex_height + vertical_spacing * (self.rows - 1))

            case GridType.FLAT_TOP_EVEN_Q:
                w_radius = target_width / ((self.cols - 1) * horizontal_spacing + hex_width)
                h_radius = target_height / ((self.rows + 0.5) * hex_height)

                radius = min(w_radius, h_radius)
                total_width = radius * (hex_width + horizontal_spacing * (self.cols - 1))
                total_height = radius * hex_height * (self.rows + 0.5)

            case GridType.FLAT_TOP_ODD_Q:
                w_radius = target_width / ((self.cols - 1) * horizontal_spacing + hex_width)
                h_radius = target_height / ((self.rows + 0.5) * hex_height)

                radius = min(w_radius, h_radius)
                total_width = radius * (hex_width + horizontal_spacing * (self.cols - 1))
                total_height = radius * hex_height * (self.rows + 0.5)

        offset_x = self.dest_rect.x + (self.dest_rect.w - total_width) / 2
        offset_y = self.dest_rect.y + (self.dest_rect.h - total_height) / 2

        return radius, offset_x, offset_y


    def get_hex_center(self, row: int, col: int) -> tuple[int, int]:
        hex_width, hex_height, horizontal_spacing, vertical_spacing = self._get_hex_geomatry()

        match self.grid_type:
            case GridType.POINTY_TOP_EVEN_R:
                x_line_factor = 0.5 if (self.rows == 1 or row % 2 == 1) else 1

                x = self.offset_x + self.radius * hex_width * (x_line_factor + col)
                y = self.offset_y + self.radius * (1 + vertical_spacing * row)

            case GridType.POINTY_TOP_ODD_R:
                x_line_factor = 0.5 if row % 2 == 0 else 1

                x = self.offset_x + self.radius * hex_width * (x_line_factor + col)
                y = self.offset_y + self.radius * (1 + vertical_spacing * row)

            case GridType.FLAT_TOP_EVEN_Q:
                y_line_factor = 0.5 if col % 2 == 1 else 0

                x = self.offset_x + self.radius * (1 + horizontal_spacing * col)
                y = self.offset_y + self.radius * hex_height * (0.5 + y_line_factor + row)

            case GridType.FLAT_TOP_ODD_Q:
                y_line_factor = 0.5 if col % 2 == 0 else 0

                x = self.offset_x + self.radius * (1 + horizontal_spacing * col)
                y = self.offset_y + self.radius * hex_height * (0.5 + y_line_factor + row)
        
        return int(x), int(y)


    def update(self):
        """Update mouse hover and click state"""
        mouse_pos = (GetMouseX(), GetMouseY())
        self.hovered_hex_coords = self._point_to_hex(*mouse_pos)
        
        # Handle click
        if IsMouseButtonPressed(MOUSE_BUTTON_LEFT) and self.hovered_hex_coords:
            row, col = self.hovered_hex_coords
            print(f"Clicked hex at row: {row}, col: {col}")
        

    def draw(self):
        """Draw the hex grid with hover effect"""
        SIDES = 6
        rotation = 30 if self.grid_type in [GridType.POINTY_TOP_EVEN_R, GridType.POINTY_TOP_ODD_R] else 0
        
        for r, row in enumerate(self.hexs):
            for c, hexcell in enumerate(row):
                # Draw filled hex if this is the hovered cell
                if self.hovered_hex_coords and (r, c) == self.hovered_hex_coords:
                    DrawPoly((hexcell.cx, hexcell.cy), SIDES, self.radius, rotation, VIOLET)
                
                # Draw outline
                DrawPolyLines((hexcell.cx, hexcell.cy), SIDES, self.radius, rotation, VIOLET)



def setup():
    grid_type = GridType.FLAT_TOP_EVEN_Q
    #grid_type = GridType.POINTY_TOP_EVEN_R
    rows = 4 
    cols = 6
    # Create grid in specific rectangle
    #grid_rect = PositionRect(50, 50, 800, 600)  # Left margin: 50px, Top margin: 50px
    grid_rect = PositionRect(50, 50, *HexGrid.calculate_rect_size(60, grid_type, rows, cols))  # Left margin: 50px, Top margin: 50px
    #grid = HexGrid(1, 2, grid_rect, GridType.FLAT_TOP_ODD_Q)  # Using POINTY_TOP_EVEN_R for H3-style
    grid = HexGrid(rows, cols, grid_rect, grid_type)  # Using POINTY_TOP_EVEN_R for H3-style
    
    return grid


def update(grid):
    grid.update()


def draw(grid):
        BeginDrawing()
        
        ClearBackground(RAYWHITE)
        DrawRectangleLines(grid.dest_rect.x, grid.dest_rect.y, grid.dest_rect.w, grid.dest_rect.h, BLUE)
        grid.draw()

        EndDrawing()


def main():
    InitWindow(1200, 800, b"Hex Grid with DrawPoly")
    SetTargetFPS(60)
    
    grid = setup()
    while not WindowShouldClose():
        update(grid)
        draw(grid)
           
    CloseWindow()


if __name__ == "__main__":
    main()

