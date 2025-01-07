# all math is explain in https://www.redblobgames.com/grids/hexagons/

from raylib import *
import math
from dataclasses import dataclass
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


@dataclass
class HexCell:
    row: int 
    col: int
    cx: int
    cy: int
    passable: bool = True
    monster: Optional[Monster] = None

class GridType(Enum):
    POINTY_TOP_EVEN_R = 1 #H3 combat type
    POINTY_TOP_ODD_R = 2
    FLAT_TOP_EVEN_Q = 3
    FLAT_TOP_ODD_Q = 4

class HexGrid:
    def __init__(self, rows: int, cols: int, dest_rect: PositionRect, grid_type: GridType):
        self.dest_rect = dest_rect 
        self.rows = rows 
        self.cols = cols 
        self.grid_type = grid_type

        self.radius, self.offset_x, self.offset_y = self._calculate_hex_radius_and_xy_offsets()

        self.hexs = [[HexCell(r, c, *self.get_hex_center(r, c)) for c in range(self.cols)] for r in range(self.rows)]

    @staticmethod
    def calculate_rect_size(radius: float, grid_type: GridType, rows: int, cols: int):
        """
        Calculate the minimum rectangle size needed to fit a hex grid with given parameters.
        Returns calculated w,h
        """
        match grid_type:
            case GridType.POINTY_TOP_EVEN_R | GridType.POINTY_TOP_ODD_R:
                hex_height = 2
                hex_width = math.sqrt(3)
                vertical_spacing = 3/4 * hex_height
                
                if rows == 1:
                    total_width = radius * hex_width * cols
                else:
                    total_width = radius * hex_width * (cols + 0.5)
                total_height = radius * (hex_height + vertical_spacing * (rows - 1))
                
            case GridType.FLAT_TOP_EVEN_Q | GridType.FLAT_TOP_ODD_Q:
                hex_width = 2
                hex_height = math.sqrt(3)
                horizontal_spacing = 3/4 * hex_width
                
                total_width = radius * (hex_width + horizontal_spacing * (cols - 1))
                total_height = radius * hex_height * (rows + 0.5)
        
        return int(total_width), int(total_height)


    def _calculate_hex_radius_and_xy_offsets(self):
        target_height, target_width = self.dest_rect.size()

        match self.grid_type:
            case GridType.POINTY_TOP_EVEN_R:
                hex_height = 2
                hex_width = math.sqrt(3)
                vertical_spacing = 3/4 * hex_height 
                horizontal_spacing = hex_width 

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
                hex_height = 2
                hex_width = math.sqrt(3)
                vertical_spacing = 3/4 * hex_height
                horizontal_spacing = hex_width

                w_radius = target_width / ((self.cols + 0.5) * hex_width)
                h_radius = target_height / ((self.rows - 1) * vertical_spacing + hex_height)

                radius = min(w_radius, h_radius)
                total_width = radius * hex_width * (self.cols + 0.5)
                total_height = radius * (hex_height + vertical_spacing * (self.rows - 1))

            case GridType.FLAT_TOP_EVEN_Q:
                hex_width = 2
                hex_height = math.sqrt(3)
                horizontal_spacing = 3/4 * hex_width
                vertical_spacing = hex_height

                w_radius = target_width / ((self.cols - 1) * horizontal_spacing + hex_width)
                h_radius = target_height / ((self.rows + 0.5) * hex_height)

                radius = min(w_radius, h_radius)
                total_width = radius * (hex_width + horizontal_spacing * (self.cols - 1))
                total_height = radius * hex_height * (self.rows + 0.5)

            case GridType.FLAT_TOP_ODD_Q:
                hex_width = 2
                hex_height = math.sqrt(3)
                horizontal_spacing = 3/4 * hex_width
                vertical_spacing = hex_height

                w_radius = target_width / ((self.cols - 1) * horizontal_spacing + hex_width)
                h_radius = target_height / ((self.rows + 0.5) * hex_height)

                radius = min(w_radius, h_radius)
                total_width = radius * (hex_width + horizontal_spacing * (self.cols - 1))
                total_height = radius * hex_height * (self.rows + 0.5)

        offset_x = self.dest_rect.x + (self.dest_rect.w - total_width) / 2
        offset_y = self.dest_rect.y + (self.dest_rect.h - total_height) / 2

        return radius, offset_x, offset_y

    def get_hex_center(self, row: int, col: int) -> tuple[int, int]:
        match self.grid_type:
            case GridType.POINTY_TOP_EVEN_R:
                hex_height = 2
                hex_width = math.sqrt(3)
                vertical_spacing = 3/4 * hex_height 
                horizontal_spacing = hex_width 
                x_line_factor = 0.5 if (self.rows == 1 or row % 2 == 1) else 1

                x = self.offset_x + self.radius * hex_width * (x_line_factor + col)
                y = self.offset_y + self.radius * (1 + vertical_spacing * row)

            case GridType.POINTY_TOP_ODD_R:
                hex_height = 2
                hex_width = math.sqrt(3)
                vertical_spacing = 3/4 * hex_height
                horizontal_spacing = hex_width
                x_line_factor = 0.5 if row % 2 == 0 else 1

                x = self.offset_x + self.radius * hex_width * (x_line_factor + col)
                y = self.offset_y + self.radius * (1 + vertical_spacing * row)

            case GridType.FLAT_TOP_EVEN_Q:
                hex_width = 2
                hex_height = math.sqrt(3)
                horizontal_spacing = 3/4 * hex_width
                vertical_spacing = hex_height
                y_line_factor = 0.5 if col % 2 == 1 else 0

                x = self.offset_x + self.radius * (1 + horizontal_spacing * col)
                y = self.offset_y + self.radius * hex_height * (0.5 + y_line_factor + row)

            case GridType.FLAT_TOP_ODD_Q:
                hex_width = 2
                hex_height = math.sqrt(3)
                horizontal_spacing = 3/4 * hex_width
                vertical_spacing = hex_height
                y_line_factor = 0.5 if col % 2 == 0 else 0

                x = self.offset_x + self.radius * (1 + horizontal_spacing * col)
                y = self.offset_y + self.radius * hex_height * (0.5 + y_line_factor + row)
        
        return int(x), int(y)

    def draw(self):
        SIDES = 6
        rotation = 30 if self.grid_type in [GridType.POINTY_TOP_EVEN_R, GridType.POINTY_TOP_ODD_R] else 0
        for r, row in enumerate(self.hexs):
            for c, hexcell in enumerate(row):
                DrawPolyLines((hexcell.cx, hexcell.cy), SIDES, self.radius, rotation, VIOLET)


def main():
    InitWindow(1200, 800, b"Hex Grid with DrawPoly")
    SetTargetFPS(60)
    
    # Create grid in specific rectangle
    #grid_rect = PositionRect(50, 50, 800, 600)  # Left margin: 50px, Top margin: 50px
    grid_rect = PositionRect(50, 50, *HexGrid.calculate_rect_size(40, GridType.POINTY_TOP_EVEN_R, 11, 15))  # Left margin: 50px, Top margin: 50px
    #grid = HexGrid(1, 2, grid_rect, GridType.FLAT_TOP_ODD_Q)  # Using POINTY_TOP_EVEN_R for H3-style
    grid = HexGrid(11, 15, grid_rect, GridType.POINTY_TOP_EVEN_R)  # Using POINTY_TOP_EVEN_R for H3-style
    
    while not WindowShouldClose():
        BeginDrawing()
        
        ClearBackground(RAYWHITE)
        DrawRectangleLines(grid_rect.x, grid_rect.y, grid_rect.w, grid_rect.h, BLUE)
        grid.draw()

        EndDrawing()
    
    CloseWindow()


if __name__ == "__main__":
    main()

