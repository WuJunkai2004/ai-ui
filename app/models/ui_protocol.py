from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class UIComponent(BaseModel):
    id: str = Field(..., description="Unique identifier for the component")
    label: str = Field(..., description="Label to display to the user")
    type: str = Field(..., description="Type of the component")
    description: Optional[str] = None


class Input(UIComponent):
    type: Literal["Input"] = "Input"
    placeholder: Optional[str] = None
    default_value: Optional[str] = None


class SelectOption(BaseModel):
    label: str
    value: Any


class Select(UIComponent):
    type: Literal["Select"] = "Select"
    options: List[SelectOption]
    default_value: Optional[Any] = None


class DatePicker(UIComponent):
    type: Literal["DatePicker"] = "DatePicker"
    range: bool = False  # If true, acts as DateRangePicker


class MultiSelect(UIComponent):
    type: Literal["MultiSelect"] = "MultiSelect"
    options: List[SelectOption]
    default_values: Optional[List[Any]] = None


class Button(UIComponent):
    type: Literal["Button"] = "Button"
    action: str = Field(..., description="Action identifier to trigger")
    variant: Optional[str] = "primary"


class MapPin(UIComponent):
    type: Literal["MapPin"] = "MapPin"
    default_lat: Optional[float] = None
    default_lng: Optional[float] = None


class RangeSlider(UIComponent):
    type: Literal["RangeSlider"] = "RangeSlider"
    min: float
    max: float
    step: Optional[float] = 1.0
    default_min: Optional[float] = None
    default_max: Optional[float] = None
    unit: Optional[str] = None


class VisualOption(BaseModel):
    image_url: str
    value: Any
    label: Optional[str] = None


class VisualPicker(UIComponent):
    type: Literal["VisualPicker"] = "VisualPicker"
    options: List[VisualOption]
    multi_select: bool = False


class Stepper(UIComponent):
    type: Literal["Stepper"] = "Stepper"
    min: float = 0
    max: float = 100
    step: float = 1
    default_value: float = 0


class Switch(UIComponent):
    type: Literal["Switch"] = "Switch"
    default_value: bool = False


# Union of all component types
ComponentType = Union[
    Input,
    Select,
    DatePicker,
    MultiSelect,
    Button,
    MapPin,
    RangeSlider,
    VisualPicker,
    Stepper,
    Switch,
]


class UIResponse(BaseModel):
    components: List[ComponentType] = Field(
        default_factory=list, description="List of UI components to render"
    )
    message: Optional[str] = Field(
        None, description="Direct answer or explanation if no UI is needed"
    )
