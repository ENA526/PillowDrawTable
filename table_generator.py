# table has
## line type
## width
## height
## outer left, right, top, bottom margin
## cell inner left, right, top, bottom margin
## font size

# restrictions can apply according to priority
## if table size > margin > font size
## then table size and margin will be fixed and font size will change accordingly
## if table size > font size > margin
## then table size and font size will be fixed and margin will change accordingly. This can have some problems if the text does not fit

# 5x5 table
# --------------------------  <- 1st row top border / table top border
# | A1 | B1 | C1 | D1 | E1 |
# |------------------------|  <- 1st row bottom border / B row top border
# |    | B2 | C2 | D2 | E2 |
# | A2 |-------------------|
# |    | B3 | C3 |   D3    |  |
# |------------------------| ^
# | A4 | B4 | C4 | D4 | E4 | Table right margin
# --------------------------
# ^                   ^    ^
# |                   |    Column E right border / table right border
# |                   Column D right border / column E left border
# Column A left border / table left border
#
#
# ---------------------------------------------------------- <- Cell <indicator> top border
# |                    Cell top margin                     |
# | Cell left margin         Text        Cell right margin |
# |                   Cell Bottom margin                   |
# ---------------------------------------------------------- <- Cell <indicator> bottom border / bottom cell's top border
#
# Cell borders will overwrite each other depending on what is declared first. The later will overwrite the former.
#

# Text Mode
## Shrink to fit
## vertical
## Wrap
## Allow new line

# table: list of rows
# row: list of cells
# cell: list
## Index 1 Content Information, List: Content, fontStyle, TextStyle, TextColor, Alignment, Rotation, Opacity
## Index 2 Cell size, Tuple: (row, column)
## Index 3 Border Style, List: (TopBorderStyle, TopBorderWitdh, TopBorderColor, TopBorderOpacity, Priority) <- for all 4 sides. Priority is for competition with neighboring cell
## Index 4 Margin, List: TopMargin, BottomMargin, LeftMargin, RightMargin


import PIL
import sys
import os
import re
class TableGenerator():
    def __init__(
            self,
            size,
            content_table=[],
            merge_request=[],
            general_font="arial",
            general_style="normal",
            general_color="black",
            general_rotation=0,
            general_opacity=100,
            general_table_outer_margin=[],
            general_cell_inner_margin=[]):
        self.size = size
        self.merge_info = []
        self.table = self._generate_plane_table_object()
    
    def add_content(self, content_object, cell_indicator=None):
        if type(content_object) == str:
            if cell_indicator is not None:
                # cell indicator can be a range or one cell ["A1:C3", "C5", "Z2", "A", "2"] -> range, single cell, column only, row only
                validation = self._cell_indicator(cell_indicator)
                match validation[0]:
                    case "range":
                        pass
            else:
                print("Target cell must be provided to insert content.")
                sys.exit(1)
            
        elif type(content_object) == list:
            pass
        else:
            print("Invalid content information.")
            sys.exit(1)

    def add_content_cell(self, content, cell_address):
        self.table[cell_address[0]][cell_address[1]][0][0] = content
        return self.table
 
    def _generate_plane_table_object(self):
        table = []
        row_number = self.size[0]
        column_number = self.size[1]
        for _ in range(row_number):
            row = []
            for _ in range(column_number):
                cell = [
                    ["", ""], # Content Information
                    (1, 1),
                    [],
                    []
                ]
                row.append(cell)
            table.append(row)
        return table
    
    def merge(self, merge_request_object):
        validation = self._merge_validation(merge_request_object)
        if validation:
            if type(merge_request_object) == str:
                self._merge_cell(merge_request_object)
                return self.table
            elif type(merge_request_object) == list:
                for merge_request in merge_request_object:
                    self._merge_cell(merge_request)
                return self.table
        else:
            raise ValueError("Invalid merge request.")
        
    def _merge_validation(self, merge_request_object):
        if type(merge_request_object) is list:
            for merge_request in merge_request_object:
                merge_request_parsed = self._cell_indicator(merge_request)
                if merge_request_parsed == "notValid" or merge_request_parsed[0] != "range":
                    return False
                request_area = merge_request_parsed[1]

                for merged_area in self.merge_info:
                    overlap = self._area_overlap(request_area, merged_area)
                    if overlap:
                        print(f"{merge_request} does overlap with {merged_area}")
                        return False
                    else:
                        print(f"{merge_request} does not overlap with {merged_area}")
            for i in range(len(merge_request_object)):
                for j in range(i + 1, len(merge_request_object)):
                    merge_request_1_parsed = self._cell_indicator(merge_request_object[i])
                    merge_request_2_parsed = self._cell_indicator(merge_request_object[j])

                    if not (merge_request_1_parsed != "notValid" and merge_request_2_parsed != "notValid" and merge_request_1_parsed[0] == "range" and merge_request_2_parsed[0] == "range"):
                        return False

                    overlap = self._area_overlap(merge_request_1_parsed[1], merge_request_2_parsed[1])
                    if overlap:
                        print(f"{merge_request_object[i]} does overlap with {merge_request_object[j]}")
                        return False
                    else:
                        print(f"{merge_request_object[i]} does not overlap with {merge_request_object[j]}")
            return True
        elif type(merge_request_object) is str:
            merge_request_parsed = self._cell_indicator(merge_request_object)
            if merge_request_parsed == "notValid" or merge_request_parsed[0] != "range":
                return False
            request_area = merge_request_parsed[1]

            for merged_area in self.merge_info:
                overlap = self._area_overlap(request_area, merged_area)
                if overlap:
                    print(f"{merge_request_object} does overlap with {merged_area}")
                    return False
                else:
                    print(f"{merge_request_object} does not overlap with {merged_area}")
            return True
        
    def _merge_cell(self, merge_request):
        merge_area = self._cell_indicator(merge_request)[1]

        top_left, size = self._find_top_left_and_size(merge_area)

        for i in range(size[0]):
            for k in range(size[1]):
                if i == 0 and k == 0:
                    self.table[top_left[0]][top_left[1]][1] = size
                else:
                    self.table[top_left[0]+i][top_left[1]+k][1] = (0, 0)
        self.merge_info.append(merge_area)
        
    def _find_top_left_and_size(self, point):
        point1 = point[0]
        point2 = point[1]
        top_left = (min(point1[0], point2[0]), min(point1[1], point2[1]))

        size = (abs(point2[0] - point1[0]) + 1, abs(point2[1] - point1[1]) + 1)

        return top_left, size

    def _area_overlap(self, area1, area2):
        overlap = not (area2[0][0] > area1[1][0] or
                       area2[1][0] < area1[0][0] or
                       area2[0][1] > area1[1][1] or
                       area2[1][1] < area1[0][1])
        return overlap

    def _cell_indicator(self, cell_indicator): # ["A1:C3", "C5", "Z2", "A", "2"] does validation as well
        if type(cell_indicator) != str:
            return "notValid"
        if ":" in cell_indicator:
            try:
                cell_range = self._cell_range_to_list(cell_indicator)
            except ValueError:
                return "notValid"
            for coordinate in cell_range:
                if (not (coordinate[0] <= self.size[0] and coordinate[1] <= self.size[1])):
                    return "notValid"
            return "range", cell_range
        elif cell_indicator.isalpha():
            column_number = self._column_name_to_number(cell_indicator)
            if column_number > self.size[0]:
                return "notValid"
            return "column", column_number
        elif cell_indicator.isdigit(): # row number
            if int(cell_indicator) > self.size[0]:
                return "notValid"
            return "row", int(cell_indicator)
        else:
            cell_tuple = self._cell_name_to_tuple(cell_indicator)
            if not (cell_tuple[0] <= self.size[0] and cell_tuple[1] <= self.size[1]):
                return "notValid"
            return "cell", cell_tuple

    def _cell_range_to_list(self, range):
        if type(range) == str and ":" in range:
            points = range.split(":")
            try:
                first = self._cell_name_to_tuple(points[0])
                second = self._cell_name_to_tuple(points[1])
                return [first, second]
            except:
                raise ValueError("Invalid range.")
        else:
            raise ValueError("Invalid range.")

    def _cell_name_to_tuple(self, cell_name):
        match = re.match(r"([a-zA-Z]+)([0-9]+)", cell_name)
        if match:
            row = self._column_name_to_number(match.group(1))
            column = int(match.group(2))
            return (column, row)
        else:
            raise ValueError("Invalid cell name format.")

    def _column_name_to_number(self, alpha_string):
        base = ord('A') - 1  # ASCII value of 'A' minus 1
        result = 0
        for char in alpha_string:
            result = result * 26 + (ord(char) - base)
        return result    

if __name__ == "__main__":
    tablegen = TableGenerator((8,8))
    tablegen.merge_info = [
        [(2,3), (2,4)],
        [(4,5), (1,2)],
        [(6,7), (8,8)]
    ] # ["A1:A3", "B3:C2"]
    #table2 = tablegen._cell_indicator_validation("A1:A3")
    table2 = tablegen.merge("A1:A3")
    # print(table2) # ["A1:C3", "C5", "B2", "A", "2"]
    #table2 = tablegen._cell_indicator("C")
    #print(table2)
    print('\n'.join(map(str, tablegen.table)))
    