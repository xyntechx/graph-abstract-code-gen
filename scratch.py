from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from enum import Enum
import uuid
import random
import math


class BlockType(Enum):
    """Types of Scratch blocks"""

    HAT = "hat"
    STACK = "stack"
    BOOLEAN = "boolean"
    REPORTER = "reporter"
    C_BLOCK = "c_block"
    CAP = "cap"


class ScratchBlock(ABC):
    """Base class for all Scratch blocks"""

    def __init__(self, opcode: str, block_type: BlockType):
        self.id = str(uuid.uuid4())
        self.opcode = opcode
        self.block_type = block_type
        self.inputs = {}
        self.fields = {}
        self.next_block = None
        self.parent = None
        self.children = []

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute the block's functionality"""
        pass

    def connect_next(self, next_block: "ScratchBlock"):
        """Connect this block to the next block in sequence"""
        self.next_block = next_block
        if next_block:
            next_block.parent = self

    def add_input(self, name: str, value: Union["ScratchBlock", Any]):
        """Add an input to this block"""
        self.inputs[name] = value
        if isinstance(value, ScratchBlock):
            value.parent = self
            self.children.append(value)

    def add_field(self, name: str, value: Any):
        """Add a field to this block"""
        self.fields[name] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary representation"""
        return {
            "id": self.id,
            "opcode": self.opcode,
            "type": self.block_type.value,
            "inputs": {
                k: v.id if isinstance(v, ScratchBlock) else v
                for k, v in self.inputs.items()
            },
            "fields": self.fields,
            "next": self.next_block.id if self.next_block else None,
            "parent": self.parent.id if self.parent else None,
        }


class WhenFlagClickedBlock(ScratchBlock):
    def __init__(self):
        super().__init__("event_whenflagclicked", BlockType.HAT)

    def execute(self, context):
        return "Program started"


class WhenKeyPressedBlock(ScratchBlock):
    def __init__(self, key_option: str):
        super().__init__("event_whenkeypressed", BlockType.HAT)
        self.add_field("KEY_OPTION", key_option)

    def execute(self, context):
        return f"Key {self.fields['KEY_OPTION']} pressed"


class MoveStepsBlock(ScratchBlock):
    def __init__(self, steps: Union[int, "ScratchBlock"]):
        super().__init__("motion_movesteps", BlockType.STACK)
        self.add_input("STEPS", steps)

    def execute(self, context):
        steps = self.inputs["STEPS"]
        if isinstance(steps, ScratchBlock):
            steps = steps.execute(context)

        direction_rad = math.radians(context.get("direction", 0))
        dx = int(steps) * math.cos(direction_rad)
        dy = int(steps) * math.sin(direction_rad)

        context["x"] = context.get("x", 0) + dx
        context["y"] = context.get("y", 0) + dy
        return f"Moved {steps} steps"


class TurnRightBlock(ScratchBlock):
    def __init__(self, degrees: Union[int, "ScratchBlock"]):
        super().__init__("motion_turnright", BlockType.STACK)
        self.add_input("DEGREES", degrees)

    def execute(self, context):
        degrees = self.inputs["DEGREES"]
        if isinstance(degrees, ScratchBlock):
            degrees = degrees.execute(context)
        context["direction"] = (context.get("direction", 0) + int(degrees)) % 360
        return f"Turned right {degrees} degrees"


class TurnLeftBlock(ScratchBlock):
    def __init__(self, degrees: Union[int, "ScratchBlock"]):
        super().__init__("motion_turnleft", BlockType.STACK)
        self.add_input("DEGREES", degrees)

    def execute(self, context):
        degrees = self.inputs["DEGREES"]
        if isinstance(degrees, ScratchBlock):
            degrees = degrees.execute(context)
        context["direction"] = (context.get("direction", 0) - int(degrees)) % 360
        return f"Turned left {degrees} degrees"


class GoToRandomBlock(ScratchBlock):
    def __init__(self):
        super().__init__("motion_goto_random", BlockType.STACK)

    def execute(self, context):
        x = random.randint(-240, 240)
        y = random.randint(-180, 180)
        context["x"] = x
        context["y"] = y
        return f"Moved to random position ({x}, {y})"


class GotoXYBlock(ScratchBlock):
    def __init__(self, x: Union[int, "ScratchBlock"], y: Union[int, "ScratchBlock"]):
        super().__init__("motion_gotoxy", BlockType.STACK)
        self.add_input("X", x)
        self.add_input("Y", y)

    def execute(self, context):
        x = self.inputs["X"]
        y = self.inputs["Y"]
        if isinstance(x, ScratchBlock):
            x = x.execute(context)
        if isinstance(y, ScratchBlock):
            y = y.execute(context)
        context["x"] = int(x)
        context["y"] = int(y)
        return f"Moved to ({x}, {y})"


class GlideToRandomBlock(ScratchBlock):
    def __init__(self, secs: Union[int, "ScratchBlock"]):
        super().__init__("motion_glideto_random", BlockType.STACK)
        self.add_input("SECS", secs)

    def execute(self, context):
        secs = self.inputs["SECS"]
        if isinstance(secs, ScratchBlock):
            secs = secs.execute(context)

        x = random.randint(-240, 240)
        y = random.randint(-180, 180)
        context["x"] = x
        context["y"] = y
        return f"Glided to random position ({x}, {y}) in {secs} seconds"


class GlideToXYBlock(ScratchBlock):
    def __init__(
        self,
        secs: Union[int, "ScratchBlock"],
        x: Union[int, "ScratchBlock"],
        y: Union[int, "ScratchBlock"],
    ):
        super().__init__("motion_glidetoxy", BlockType.STACK)
        self.add_input("SECS", secs)
        self.add_input("X", x)
        self.add_input("Y", y)

    def execute(self, context):
        secs = self.inputs["SECS"]
        x = self.inputs["X"]
        y = self.inputs["Y"]

        if isinstance(secs, ScratchBlock):
            secs = secs.execute(context)
        if isinstance(x, ScratchBlock):
            x = x.execute(context)
        if isinstance(y, ScratchBlock):
            y = y.execute(context)

        context["x"] = int(x)
        context["y"] = int(y)
        return f"Glided to ({x}, {y}) in {secs} seconds"


class PointInDirectionBlock(ScratchBlock):
    def __init__(self, direction: Union[int, "ScratchBlock"]):
        super().__init__("motion_pointindirection", BlockType.STACK)
        self.add_input("DIRECTION", direction)

    def execute(self, context):
        direction = self.inputs["DIRECTION"]
        if isinstance(direction, ScratchBlock):
            direction = direction.execute(context)
        context["direction"] = int(direction) % 360
        return f"Pointed in direction {direction}"


class ChangeXByBlock(ScratchBlock):
    def __init__(self, dx: Union[int, "ScratchBlock"]):
        super().__init__("motion_changexby", BlockType.STACK)
        self.add_input("DX", dx)

    def execute(self, context):
        dx = self.inputs["DX"]
        if isinstance(dx, ScratchBlock):
            dx = dx.execute(context)
        context["x"] = context.get("x", 0) + int(dx)
        return f"Changed x by {dx}"


class SetXToBlock(ScratchBlock):
    def __init__(self, x: Union[int, "ScratchBlock"]):
        super().__init__("motion_setx", BlockType.STACK)
        self.add_input("X", x)

    def execute(self, context):
        x = self.inputs["X"]
        if isinstance(x, ScratchBlock):
            x = x.execute(context)
        context["x"] = int(x)
        return f"Set x to {x}"


class ChangeYByBlock(ScratchBlock):
    def __init__(self, dy: Union[int, "ScratchBlock"]):
        super().__init__("motion_changeyby", BlockType.STACK)
        self.add_input("DY", dy)

    def execute(self, context):
        dy = self.inputs["DY"]
        if isinstance(dy, ScratchBlock):
            dy = dy.execute(context)
        context["y"] = context.get("y", 0) + int(dy)
        return f"Changed y by {dy}"


class SetYToBlock(ScratchBlock):
    def __init__(self, y: Union[int, "ScratchBlock"]):
        super().__init__("motion_sety", BlockType.STACK)
        self.add_input("Y", y)

    def execute(self, context):
        y = self.inputs["Y"]
        if isinstance(y, ScratchBlock):
            y = y.execute(context)
        context["y"] = int(y)
        return f"Set y to {y}"


class XPositionBlock(ScratchBlock):
    def __init__(self):
        super().__init__("motion_xposition", BlockType.REPORTER)

    def execute(self, context):
        return context.get("x", 0)


class YPositionBlock(ScratchBlock):
    def __init__(self):
        super().__init__("motion_yposition", BlockType.REPORTER)

    def execute(self, context):
        return context.get("y", 0)


class SayBlock(ScratchBlock):
    def __init__(self, message: Union[str, "ScratchBlock"]):
        super().__init__("looks_say", BlockType.STACK)
        self.add_input("MESSAGE", message)

    def execute(self, context):
        message = self.inputs["MESSAGE"]
        if isinstance(message, ScratchBlock):
            message = message.execute(context)
        return f"Says: {message}"


class SayForSecsBlock(ScratchBlock):
    def __init__(
        self, message: Union[str, "ScratchBlock"], secs: Union[int, "ScratchBlock"]
    ):
        super().__init__("looks_sayforsecs", BlockType.STACK)
        self.add_input("MESSAGE", message)
        self.add_input("SECS", secs)

    def execute(self, context):
        message = self.inputs["MESSAGE"]
        secs = self.inputs["SECS"]
        if isinstance(message, ScratchBlock):
            message = message.execute(context)
        if isinstance(secs, ScratchBlock):
            secs = secs.execute(context)
        return f"Says '{message}' for {secs} seconds"


class ThinkBlock(ScratchBlock):
    def __init__(self, message: Union[str, "ScratchBlock"]):
        super().__init__("looks_think", BlockType.STACK)
        self.add_input("MESSAGE", message)

    def execute(self, context):
        message = self.inputs["MESSAGE"]
        if isinstance(message, ScratchBlock):
            message = message.execute(context)
        return f"Thinks: {message}"


class ThinkForSecsBlock(ScratchBlock):
    def __init__(
        self, message: Union[str, "ScratchBlock"], secs: Union[int, "ScratchBlock"]
    ):
        super().__init__("looks_thinkforsecs", BlockType.STACK)
        self.add_input("MESSAGE", message)
        self.add_input("SECS", secs)

    def execute(self, context):
        message = self.inputs["MESSAGE"]
        secs = self.inputs["SECS"]
        if isinstance(message, ScratchBlock):
            message = message.execute(context)
        if isinstance(secs, ScratchBlock):
            secs = secs.execute(context)
        return f"Thinks '{message}' for {secs} seconds"


class ChangeSizeByBlock(ScratchBlock):
    def __init__(self, change: Union[int, "ScratchBlock"]):
        super().__init__("looks_changesizeby", BlockType.STACK)
        self.add_input("CHANGE", change)

    def execute(self, context):
        change = self.inputs["CHANGE"]
        if isinstance(change, ScratchBlock):
            change = change.execute(context)
        context["size"] = context.get("size", 100) + int(change)
        return f"Changed size by {change}"


class SetSizeToBlock(ScratchBlock):
    def __init__(self, size: Union[int, "ScratchBlock"]):
        super().__init__("looks_setsizeto", BlockType.STACK)
        self.add_input("SIZE", size)

    def execute(self, context):
        size = self.inputs["SIZE"]
        if isinstance(size, ScratchBlock):
            size = size.execute(context)
        context["size"] = int(size)
        return f"Set size to {size}"


class WaitBlock(ScratchBlock):
    def __init__(self, secs: Union[int, "ScratchBlock"]):
        super().__init__("control_wait", BlockType.STACK)
        self.add_input("SECS", secs)

    def execute(self, context):
        secs = self.inputs["SECS"]
        if isinstance(secs, ScratchBlock):
            secs = secs.execute(context)
        return f"Waited {secs} seconds"


class RepeatBlock(ScratchBlock):
    def __init__(self, times: Union[int, "ScratchBlock"]):
        super().__init__("control_repeat", BlockType.C_BLOCK)
        self.add_input("TIMES", times)
        self.substack = []

    def add_to_substack(self, block: ScratchBlock):
        """Add a block to the repeat loop"""
        self.substack.append(block)
        block.parent = self
        self.children.append(block)

    def execute(self, context):
        times = self.inputs["TIMES"]
        if isinstance(times, ScratchBlock):
            times = times.execute(context)

        results = []
        for block in self.substack:
            result = block.execute(context)
            results.append(result)
        return f"Repeated {times} times: {results}"


class ForeverBlock(ScratchBlock):
    def __init__(self):
        super().__init__("control_forever", BlockType.C_BLOCK)
        self.substack = []

    def add_to_substack(self, block: ScratchBlock):
        """Add a block to the forever loop"""
        self.substack.append(block)
        block.parent = self
        self.children.append(block)

    def execute(self, context):
        results = []
        for block in self.substack:
            result = block.execute(context)
            results.append(result)
        return f"Forever loop: {results}"


class IfBlock(ScratchBlock):
    def __init__(self, condition: "ScratchBlock"):
        super().__init__("control_if", BlockType.C_BLOCK)
        self.add_input("CONDITION", condition)
        self.substack = []

    def add_to_substack(self, block: ScratchBlock):
        """Add a block to the if statement"""
        self.substack.append(block)
        block.parent = self
        self.children.append(block)

    def execute(self, context):
        condition = self.inputs["CONDITION"].execute(context)
        if condition:
            results = []
            for block in self.substack:
                result = block.execute(context)
                results.append(result)
            return f"If condition met: {results}"
        return f"If condition not met (if the condition was met: {results})"


class IfElseBlock(ScratchBlock):
    def __init__(self, condition: "ScratchBlock"):
        super().__init__("control_if_else", BlockType.C_BLOCK)
        self.add_input("CONDITION", condition)
        self.substack = []
        self.substack2 = []

    def add_to_substack(self, block: ScratchBlock):
        """Add a block to the if part"""
        self.substack.append(block)
        block.parent = self
        self.children.append(block)

    def add_to_else_substack(self, block: ScratchBlock):
        """Add a block to the else part"""
        self.substack2.append(block)
        block.parent = self
        self.children.append(block)

    def execute(self, context):
        condition = self.inputs["CONDITION"].execute(context)
        results_if = []
        results_else = []

        for block in self.substack:
            result = block.execute(context)
            results_if.append(result)
        for block in self.substack2:
            result = block.execute(context)
            results_else.append(result)

        if condition:
            return f"If condition met: {results_if} (else: {results_else})"
        else:
            return f"Else condition met: {results_else} (if: {results_if})"


class WaitUntilBlock(ScratchBlock):
    def __init__(self, condition: "ScratchBlock"):
        super().__init__("control_wait_until", BlockType.STACK)
        self.add_input("CONDITION", condition)

    def execute(self, context):
        # Simplified - would actually wait until condition is true
        condition = self.inputs["CONDITION"].execute(context)
        return f"Waited until condition: {condition}"


class RepeatUntilBlock(ScratchBlock):
    def __init__(self, condition: "ScratchBlock"):
        super().__init__("control_repeat_until", BlockType.C_BLOCK)
        self.add_input("CONDITION", condition)
        self.substack = []

    def add_to_substack(self, block: ScratchBlock):
        """Add a block to the repeat until loop"""
        self.substack.append(block)
        block.parent = self
        self.children.append(block)

    def execute(self, context):
        results = []
        for block in self.substack:
            result = block.execute(context)
            results.append(result)

        return f"Repeat until {self.inputs['CONDITION']}: {results}"


class StopBlock(ScratchBlock):
    def __init__(self, stop_option: str):
        super().__init__("control_stop", BlockType.CAP)
        self.add_field("STOP_OPTION", stop_option)

    def execute(self, context):
        return f"Stop {self.fields['STOP_OPTION']}"


class KeyPressedBlock(ScratchBlock):
    def __init__(self, key_option: str):
        super().__init__("sensing_keypressed", BlockType.BOOLEAN)
        self.add_field("KEY_OPTION", key_option)

    def execute(self, context):
        # Simplified - would check actual key state
        return context.get(f"key_{self.fields['KEY_OPTION']}", False)


class MouseDownBlock(ScratchBlock):
    def __init__(self):
        super().__init__("sensing_mousedown", BlockType.BOOLEAN)

    def execute(self, context):
        return context.get("mouse_down", False)


class AddBlock(ScratchBlock):
    def __init__(
        self, num1: Union[int, "ScratchBlock"], num2: Union[int, "ScratchBlock"]
    ):
        super().__init__("operator_add", BlockType.REPORTER)
        self.add_input("NUM1", num1)
        self.add_input("NUM2", num2)

    def execute(self, context):
        num1 = self.inputs["NUM1"]
        num2 = self.inputs["NUM2"]
        if isinstance(num1, ScratchBlock):
            num1 = num1.execute(context)
        if isinstance(num2, ScratchBlock):
            num2 = num2.execute(context)
        return float(num1) + float(num2)


class SubtractBlock(ScratchBlock):
    def __init__(
        self, num1: Union[int, "ScratchBlock"], num2: Union[int, "ScratchBlock"]
    ):
        super().__init__("operator_subtract", BlockType.REPORTER)
        self.add_input("NUM1", num1)
        self.add_input("NUM2", num2)

    def execute(self, context):
        num1 = self.inputs["NUM1"]
        num2 = self.inputs["NUM2"]
        if isinstance(num1, ScratchBlock):
            num1 = num1.execute(context)
        if isinstance(num2, ScratchBlock):
            num2 = num2.execute(context)
        return float(num1) - float(num2)


class MultiplyBlock(ScratchBlock):
    def __init__(
        self, num1: Union[int, "ScratchBlock"], num2: Union[int, "ScratchBlock"]
    ):
        super().__init__("operator_multiply", BlockType.REPORTER)
        self.add_input("NUM1", num1)
        self.add_input("NUM2", num2)

    def execute(self, context):
        num1 = self.inputs["NUM1"]
        num2 = self.inputs["NUM2"]
        if isinstance(num1, ScratchBlock):
            num1 = num1.execute(context)
        if isinstance(num2, ScratchBlock):
            num2 = num2.execute(context)
        return float(num1) * float(num2)


class DivideBlock(ScratchBlock):
    def __init__(
        self, num1: Union[int, "ScratchBlock"], num2: Union[int, "ScratchBlock"]
    ):
        super().__init__("operator_divide", BlockType.REPORTER)
        self.add_input("NUM1", num1)
        self.add_input("NUM2", num2)

    def execute(self, context):
        num1 = self.inputs["NUM1"]
        num2 = self.inputs["NUM2"]
        if isinstance(num1, ScratchBlock):
            num1 = num1.execute(context)
        if isinstance(num2, ScratchBlock):
            num2 = num2.execute(context)
        if float(num2) == 0:
            return float("inf")
        return float(num1) / float(num2)


class RandomBlock(ScratchBlock):
    def __init__(
        self, from_num: Union[int, "ScratchBlock"], to_num: Union[int, "ScratchBlock"]
    ):
        super().__init__("operator_random", BlockType.REPORTER)
        self.add_input("FROM_NUM", from_num)
        self.add_input("TO_NUM", to_num)

    def execute(self, context):
        from_num = self.inputs["FROM_NUM"]
        to_num = self.inputs["TO_NUM"]
        if isinstance(from_num, ScratchBlock):
            from_num = from_num.execute(context)
        if isinstance(to_num, ScratchBlock):
            to_num = to_num.execute(context)
        return random.randint(int(from_num), int(to_num))


class GreaterThanBlock(ScratchBlock):
    def __init__(
        self, operand1: Union[Any, "ScratchBlock"], operand2: Union[Any, "ScratchBlock"]
    ):
        super().__init__("operator_gt", BlockType.BOOLEAN)
        self.add_input("OPERAND1", operand1)
        self.add_input("OPERAND2", operand2)

    def execute(self, context):
        op1 = self.inputs["OPERAND1"]
        op2 = self.inputs["OPERAND2"]
        if isinstance(op1, ScratchBlock):
            op1 = op1.execute(context)
        if isinstance(op2, ScratchBlock):
            op2 = op2.execute(context)
        try:
            return float(op1) > float(op2)
        except ValueError:
            return str(op1) > str(op2)


class LessThanBlock(ScratchBlock):
    def __init__(
        self, operand1: Union[Any, "ScratchBlock"], operand2: Union[Any, "ScratchBlock"]
    ):
        super().__init__("operator_lt", BlockType.BOOLEAN)
        self.add_input("OPERAND1", operand1)
        self.add_input("OPERAND2", operand2)

    def execute(self, context):
        op1 = self.inputs["OPERAND1"]
        op2 = self.inputs["OPERAND2"]
        if isinstance(op1, ScratchBlock):
            op1 = op1.execute(context)
        if isinstance(op2, ScratchBlock):
            op2 = op2.execute(context)
        try:
            return float(op1) < float(op2)
        except ValueError:
            return str(op1) < str(op2)


class EqualsBlock(ScratchBlock):
    def __init__(
        self, operand1: Union[Any, "ScratchBlock"], operand2: Union[Any, "ScratchBlock"]
    ):
        super().__init__("operator_equals", BlockType.BOOLEAN)
        self.add_input("OPERAND1", operand1)
        self.add_input("OPERAND2", operand2)

    def execute(self, context):
        op1 = self.inputs["OPERAND1"]
        op2 = self.inputs["OPERAND2"]
        if isinstance(op1, ScratchBlock):
            op1 = op1.execute(context)
        if isinstance(op2, ScratchBlock):
            op2 = op2.execute(context)
        return op1 == op2


class AndBlock(ScratchBlock):
    def __init__(self, operand1: "ScratchBlock", operand2: "ScratchBlock"):
        super().__init__("operator_and", BlockType.BOOLEAN)
        self.add_input("OPERAND1", operand1)
        self.add_input("OPERAND2", operand2)

    def execute(self, context):
        op1 = self.inputs["OPERAND1"].execute(context)
        op2 = self.inputs["OPERAND2"].execute(context)
        return bool(op1) and bool(op2)


class OrBlock(ScratchBlock):
    def __init__(self, operand1: "ScratchBlock", operand2: "ScratchBlock"):
        super().__init__("operator_or", BlockType.BOOLEAN)
        self.add_input("OPERAND1", operand1)
        self.add_input("OPERAND2", operand2)

    def execute(self, context):
        op1 = self.inputs["OPERAND1"].execute(context)
        op2 = self.inputs["OPERAND2"].execute(context)
        return bool(op1) or bool(op2)


class NotBlock(ScratchBlock):
    def __init__(self, operand: "ScratchBlock"):
        super().__init__("operator_not", BlockType.BOOLEAN)
        self.add_input("OPERAND", operand)

    def execute(self, context):
        op = self.inputs["OPERAND"].execute(context)
        return not bool(op)


class JoinBlock(ScratchBlock):
    def __init__(
        self, string1: Union[str, "ScratchBlock"], string2: Union[str, "ScratchBlock"]
    ):
        super().__init__("operator_join", BlockType.REPORTER)
        self.add_input("STRING1", string1)
        self.add_input("STRING2", string2)

    def execute(self, context):
        str1 = self.inputs["STRING1"]
        str2 = self.inputs["STRING2"]
        if isinstance(str1, ScratchBlock):
            str1 = str1.execute(context)
        if isinstance(str2, ScratchBlock):
            str2 = str2.execute(context)
        return str(str1) + str(str2)


class LetterOfBlock(ScratchBlock):
    def __init__(
        self, letter_num: Union[int, "ScratchBlock"], string: Union[str, "ScratchBlock"]
    ):
        super().__init__("operator_letter_of", BlockType.REPORTER)
        self.add_input("LETTER_NUM", letter_num)
        self.add_input("STRING", string)

    def execute(self, context):
        letter_num = self.inputs["LETTER_NUM"]
        string = self.inputs["STRING"]
        if isinstance(letter_num, ScratchBlock):
            letter_num = letter_num.execute(context)
        if isinstance(string, ScratchBlock):
            string = string.execute(context)

        string = str(string)
        letter_num = int(letter_num)

        if 1 <= letter_num <= len(string):
            return string[letter_num - 1]  # 1-based indexing
        return ""


class LengthOfBlock(ScratchBlock):
    def __init__(self, string: Union[str, "ScratchBlock"]):
        super().__init__("operator_length", BlockType.REPORTER)
        self.add_input("STRING", string)

    def execute(self, context):
        string = self.inputs["STRING"]
        if isinstance(string, ScratchBlock):
            string = string.execute(context)
        return len(str(string))


class ContainsBlock(ScratchBlock):
    def __init__(
        self, string1: Union[str, "ScratchBlock"], string2: Union[str, "ScratchBlock"]
    ):
        super().__init__("operator_contains", BlockType.BOOLEAN)
        self.add_input("STRING1", string1)
        self.add_input("STRING2", string2)

    def execute(self, context):
        str1 = self.inputs["STRING1"]
        str2 = self.inputs["STRING2"]
        if isinstance(str1, ScratchBlock):
            str1 = str1.execute(context)
        if isinstance(str2, ScratchBlock):
            str2 = str2.execute(context)
        return str(str2) in str(str1)


class ModBlock(ScratchBlock):
    def __init__(
        self, num1: Union[int, "ScratchBlock"], num2: Union[int, "ScratchBlock"]
    ):
        super().__init__("operator_mod", BlockType.REPORTER)
        self.add_input("NUM1", num1)
        self.add_input("NUM2", num2)

    def execute(self, context):
        num1 = self.inputs["NUM1"]
        num2 = self.inputs["NUM2"]
        if isinstance(num1, ScratchBlock):
            num1 = num1.execute(context)
        if isinstance(num2, ScratchBlock):
            num2 = num2.execute(context)
        if float(num2) == 0:
            return float("nan")
        return float(num1) % float(num2)


class RoundBlock(ScratchBlock):
    def __init__(self, num: Union[float, "ScratchBlock"]):
        super().__init__("operator_round", BlockType.REPORTER)
        self.add_input("NUM", num)

    def execute(self, context):
        num = self.inputs["NUM"]
        if isinstance(num, ScratchBlock):
            num = num.execute(context)
        return round(float(num))


class MathFunctionBlock(ScratchBlock):
    def __init__(self, operator: str, num: Union[float, "ScratchBlock"]):
        super().__init__("operator_mathop", BlockType.REPORTER)
        self.add_field("OPERATOR", operator)
        self.add_input("NUM", num)

    def execute(self, context):
        num = self.inputs["NUM"]
        if isinstance(num, ScratchBlock):
            num = num.execute(context)

        num = float(num)
        operator = self.fields["OPERATOR"]

        try:
            if operator == "abs":
                return abs(num)
            elif operator == "floor":
                return math.floor(num)
            elif operator == "ceiling":
                return math.ceil(num)
            elif operator == "sqrt":
                return math.sqrt(num)
            elif operator == "sin":
                return math.sin(math.radians(num))
            elif operator == "cos":
                return math.cos(math.radians(num))
            elif operator == "tan":
                return math.tan(math.radians(num))
            elif operator == "asin":
                return math.degrees(math.asin(num))
            elif operator == "acos":
                return math.degrees(math.acos(num))
            elif operator == "atan":
                return math.degrees(math.atan(num))
            elif operator == "ln":
                return math.log(num)
            elif operator == "log":
                return math.log10(num)
            elif operator == "e ^":
                return math.exp(num)
            elif operator == "10 ^":
                return 10**num
            else:
                return num
        except (ValueError, ZeroDivisionError):
            return float("nan")


class SetVariableBlock(ScratchBlock):
    def __init__(self, variable: str, value: Union[Any, "ScratchBlock"]):
        super().__init__("data_setvariableto", BlockType.STACK)
        self.add_field("VARIABLE", variable)
        self.add_input("VALUE", value)

    def execute(self, context):
        var_name = self.fields["VARIABLE"]
        value = self.inputs["VALUE"]
        if isinstance(value, ScratchBlock):
            value = value.execute(context)
        context[f"var_{var_name}"] = value
        return f"Set {var_name} to {value}"


class ChangeVariableByBlock(ScratchBlock):
    def __init__(self, variable: str, value: Union[Any, "ScratchBlock"]):
        super().__init__("data_changevariableby", BlockType.STACK)
        self.add_field("VARIABLE", variable)
        self.add_input("VALUE", value)

    def execute(self, context):
        var_name = self.fields["VARIABLE"]
        value = self.inputs["VALUE"]
        if isinstance(value, ScratchBlock):
            value = value.execute(context)

        current_value = context.get(f"var_{var_name}", 0)
        try:
            new_value = float(current_value) + float(value)
        except ValueError:
            new_value = str(current_value) + str(value)

        context[f"var_{var_name}"] = new_value
        return f"Changed {var_name} by {value}"


class GetVariableBlock(ScratchBlock):
    def __init__(self, variable: str):
        super().__init__("data_variable", BlockType.REPORTER)
        self.add_field("VARIABLE", variable)

    def execute(self, context):
        var_name = self.fields["VARIABLE"]
        return context.get(f"var_{var_name}", 0)


class ScratchProgram:
    """Represents a complete Scratch program as a graph of blocks"""

    def __init__(self):
        self.blocks = {}
        self.scripts = []

    def add_block(self, block: ScratchBlock):
        """Add a block to the program"""
        self.blocks[block.id] = block

    def add_script(self, start_block: ScratchBlock):
        """Add a script (starting with a hat block)"""
        self.scripts.append(start_block)
        self._add_connected_blocks(start_block)

    def _add_connected_blocks(self, block: ScratchBlock):
        """Recursively add all connected blocks"""
        self.add_block(block)

        if block.next_block:
            self._add_connected_blocks(block.next_block)

        for child in block.children:
            self._add_connected_blocks(child)

        if hasattr(block, "substack"):
            for subblock in block.substack:
                self._add_connected_blocks(subblock)

        if hasattr(block, "substack2"):
            for subblock in block.substack2:
                self._add_connected_blocks(subblock)

    def _collect_connected_blocks(self, block: ScratchBlock, connected_blocks: set):
        """Recursively collect all blocks connected to a given block"""
        if block.id in connected_blocks:
            return

        connected_blocks.add(block.id)

        if block.next_block:
            self._collect_connected_blocks(block.next_block, connected_blocks)

        for child in block.children:
            self._collect_connected_blocks(child, connected_blocks)

        if hasattr(block, "substack"):
            for subblock in block.substack:
                self._collect_connected_blocks(subblock, connected_blocks)

        if hasattr(block, "substack2"):
            for subblock in block.substack2:
                self._collect_connected_blocks(subblock, connected_blocks)

    def execute(self, context: Optional[Dict[str, Any]] = None):
        """Execute all scripts in the program"""
        if context is None:
            context = {"x": 0, "y": 0, "direction": 0, "size": 100}

        results = []
        for script in self.scripts:
            result = self._execute_script(script, context)
            results.append(result)

        return results, context

    def _execute_script(self, block: ScratchBlock, context: Dict[str, Any]):
        """Execute a script starting from a given block"""
        results = []
        current_block = block

        while current_block:
            result = current_block.execute(context)
            results.append(result)
            current_block = current_block.next_block

        return results

    def to_dict(self) -> Dict[str, Any]:
        """Convert program to dictionary representation"""
        return {
            "blocks": {
                block_id: block.to_dict() for block_id, block in self.blocks.items()
            },
            "scripts": [script.id for script in self.scripts],
        }
