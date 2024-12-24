from dataclasses import dataclass
import tomli

@dataclass
class Building:
    name: str
    src: str
    h: int
    w: int
    x: int
    y: int

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            src=data['src'],
            h=data['h'],
            w=data['w'],
            x=data['x'],
            y=data['y'],
        )
    
    def is_in(self, x, y) -> bool:
        is_x_in = self.x < x < (self.x + self.w)
        is_y_in = self.y < y < (self.y + self.h)
        return is_x_in and is_y_in


@dataclass
class Background:
    name: str
    src: str
    w: int
    h: int
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            src=data['src'],
            w=data['w'],
            h=data['h'],
        )

@dataclass
class GameConfig:
    bg: Background
    bildings: list[Building]  # Changed to match your TOML structure
    
    @classmethod
    def load(cls, toml_file):
        with open(toml_file, 'rb') as f:
            data = tomli.load(f)
        
        return cls(
            bg=Background.from_dict(data['bg']),
            bildings=[Building.from_dict(b) for b in data['bildings']])

# Example usage
if __name__ == "__main__":
    # Load the configuration
    config = GameConfig.load("tmp.toml")
    
    # Print background info
    print("Background:")
    print(f"  Name: {config.bg.name}")
    print(f"  Source: {config.bg.src}")
    print(f"  Size: {config.bg.w}x{config.bg.h}")
    
    # Iterate over buildings
    print("\nBuildings:")
    for building in config.bildings:  # Changed to match your TOML structure
        print(f"\n  Building: {building.name}")
        print(f"  Source: {building.src}")
        print(f"  Size: {building.w}x{building.h}")
        print(f"  Position: ({building.x}, {building.y})")
