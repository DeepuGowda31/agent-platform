import ast
import operator
from app.tools.base_tool import BaseTool
from app.core.logger import logger

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}

def _safe_eval(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Unsupported expression: {type(node)}")

class CalculatorTool(BaseTool):
    name = "calculator"

    async def run(self, input_data: str) -> str:
        logger.info({"event": "CALCULATOR", "expr": input_data})
        try:
            import re
            # Handle percentage: "15% of 2400" → "2400 * 0.15"
            pct = re.search(r"(\d+\.?\d*)%\s*of\s*(\d+\.?\d*)", input_data, re.IGNORECASE)
            if pct:
                expr = f"{pct.group(2)} * {float(pct.group(1)) / 100}"
            else:
                match = re.search(r"[\d][\d\s\+\-\*\/\(\)\.\^%]*", input_data)
                if not match:
                    return f"Could not find a math expression in: {input_data}"
                expr = match.group().strip().replace("^", "**")
            if not expr:
                return f"Could not find a math expression in: {input_data}"
            tree = ast.parse(expr, mode="eval")
            result = _safe_eval(tree.body)
            return f"{expr} = {result}"
        except Exception as e:
            logger.error({"event": "CALCULATOR_ERROR", "error": str(e)})
            return f"Could not calculate: {str(e)}"
