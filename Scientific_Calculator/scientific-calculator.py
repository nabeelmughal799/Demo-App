import math
import re
import streamlit as st

FUNCS = ("asinh|acosh|atanh|sinh|cosh|tanh|asin|acos|atan|acot|sin|cos|tan|cot|sec|csc|"
         "sqrt|log|ln|exp|fact|abs|floor|ceil|pow|radians|degrees")
NUM = r"(?:\d+\.?\d*(?:[eE][-+]?\d+)?|\.\d+)"
OPERATORS = "+-×÷*/^%"

def safe_div(num, den):
    if abs(den) < 1e-12:
        raise ZeroDivisionError("undefined")
    return num / den


def build_env(mode):
    if mode == "DEG":
        to_rad = math.radians
        from_rad = math.degrees
    else:
        to_rad = lambda x: x
        from_rad = lambda x: x

    def clean_trig(value):
        if abs(value) < 1e-12:
            return 0.0
        if abs(value - 1) < 1e-12:
            return 1.0
        if abs(value + 1) < 1e-12:
            return -1.0
        return value

    sin_ = lambda x: clean_trig(math.sin(to_rad(x)))
    cos_ = lambda x: clean_trig(math.cos(to_rad(x)))

    return {
        "sin": sin_,
        "cos": cos_,
        "tan": lambda x: safe_div(sin_(x), cos_(x)),
        "cot": lambda x: safe_div(cos_(x), sin_(x)),
        "sec": lambda x: safe_div(1, cos_(x)),
        "csc": lambda x: safe_div(1, sin_(x)),
        "asin": lambda x: from_rad(math.asin(x)),
        "acos": lambda x: from_rad(math.acos(x)),
        "atan": lambda x: from_rad(math.atan(x)),
        "acot": lambda x: from_rad(math.atan2(1, x)),
        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
        "asinh": math.asinh, "acosh": math.acosh, "atanh": math.atanh,
        "log": math.log10, "ln": math.log, "sqrt": math.sqrt,
        "exp": math.exp, "fact": math.factorial, "abs": abs,
        "pow": math.pow, "floor": math.floor, "ceil": math.ceil,
        "radians": math.radians, "degrees": math.degrees,
        "pi": math.pi, "e": math.e,
    }


def prepare(text):
    text = (text.replace("×", "*").replace("÷", "/").replace("^", "**")
                .replace("π", "pi").replace("θ", "theta").replace("√", "sqrt "))
    text = re.sub(rf"({NUM})\s*%", r"(\1/100)", text)
    text = re.sub(r"(?<=[\d.)])\s*(?=[a-zA-Z(])(?![eE][-+]?\d)", "*", text)
    text = re.sub(
        rf"(?<![A-Za-z])({FUNCS})(?![A-Za-z])\s*(?!\()([-+]?(?:{NUM}|pi\b|e\b|x\b|theta\b))",
        r"\1(\2)", text)
    text = re.sub(r"\b(pi|e|x|theta)\b\s*(?=[\d(a-zA-Z])", r"\1*", text)
    return text + ")" * (text.count("(") - text.count(")"))


def safe_eval(text, env, extra=None):
    if "__" in text or len(text) > 300:
        raise ValueError("not allowed")
    scope = {"__builtins__": {}, **env}
    if extra:
        scope.update(extra)
    result = eval(prepare(text), scope)
    if isinstance(result, complex) or not isinstance(result, (int, float)):
        raise ValueError("not a number")
    return result


def fmt(value, digits=10, tol=1e-12):
    if abs(value) < tol:
        return "0"
    return f"{value:.{digits}g}"


def evaluate(text, mode):
    try:
        return fmt(safe_eval(text, build_env(mode))), ""
    except ZeroDivisionError:
        return "", "Error: undefined / zero se divide"
    except Exception:
        return "", "Error: expression sahi nahi"


def derivative(f, x, h=1e-3):
    return (-f(x + 2*h) + 8*f(x + h) - 8*f(x - h) + f(x - 2*h)) / (12 * h)


def second_derivative(f, x, h=1e-3):
    return (f(x + h) - 2 * f(x) + f(x - h)) / h**2


def integrate(f, a, b, n=2000):
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += (4 if i % 2 else 2) * f(a + i * h)
    return total * h / 3


st.set_page_config(page_title="Scientific Calculator", page_icon="🧮")

defaults = {"expr": "", "ans": "", "done_expr": None, "error_for": None,
            "history": []}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value
def finish():
    s = st.session_state
    if not s.expr.strip() or s.done_expr == s.expr:
        return
    value, error = evaluate(s.expr, s.mode)
    if error:
        s.error_for = s.expr
        return
    s.ans = value
    s.done_expr = s.expr
    s.history.append(f"{s.expr} = {value}")


def press(key):
    s = st.session_state
    if key == "C":
        s.expr = ""
        s.done_expr = None
        return
    if key == "DEL":
        s.expr = re.sub(r"(?:[a-z]+\(?\s*|.)$", "", s.expr)
        s.done_expr = None
        return
    if key == "=":
        finish()
        return
    text = s.ans if key == "ANS" else key
    if not text:
        return
    if s.done_expr is not None and s.expr == s.done_expr:
        is_operator = key != "ANS" and text[0] in OPERATORS
        s.expr = s.ans + text if is_operator else text
    else:
        s.expr += text
    s.done_expr = None


BUTTONS = [
    [("sin", "sin "), ("cos", "cos "), ("tan", "tan "), ("cot", "cot "), ("sec", "sec ")],
    [("csc", "csc "), ("sin⁻¹", "asin "), ("cos⁻¹", "acos "), ("tan⁻¹", "atan "), ("cot⁻¹", "acot ")],
    [("sinh", "sinh "), ("cosh", "cosh "), ("tanh", "tanh "), ("log", "log "), ("ln", "ln ")],
    [("√", "sqrt "), ("x²", "^2"), ("xʸ", "^"), ("n!", "fact "), ("exp", "exp ")],
    [("π", "pi"), ("e", "e"), ("(", "("), (")", ")"), ("%", "%")],
    [("7", "7"), ("8", "8"), ("9", "9"), ("÷", "÷"), ("DEL", "DEL")],
    [("4", "4"), ("5", "5"), ("6", "6"), ("×", "×"), ("C", "C")],
    [("1", "1"), ("2", "2"), ("3", "3"), ("−", "-"), ("ANS", "ANS")],
    [("0", "0"), (".", "."), ("abs", "abs "), ("+", "+"), ("=", "=")],
]
MORE_BUTTONS = [
    [("asinh", "asinh "), ("acosh", "acosh "), ("atanh", "atanh "), ("floor", "floor "), ("ceil", "ceil ")],
    [("pow", "pow("), ("radians", "radians "), ("degrees", "degrees ")],
]

st.title("Scientific Calculator")
web_module, = st.tabs(["Web Calculator"])
with web_module:
    tab1, tab2, tab3 = st.tabs(["Calculator", "Trigonometry", "Calculus"])

with tab1:
    st.radio("Angle mode", ["DEG", "RAD"], horizontal=True, key="mode")
    st.text_input("Expression", key="expr")

    if st.session_state.expr.strip():
        shown, error = evaluate(st.session_state.expr, st.session_state.mode)
    else:
        shown, error = "", ""
    if shown:
        st.markdown(f"### = {shown}")
    elif error and st.session_state.error_for == st.session_state.expr:
        st.error(error)

    for r, row in enumerate(BUTTONS):
        cols = st.columns(len(row))
        for c, (label, value) in enumerate(row):
            cols[c].button(label, key=f"btn_{r}_{c}", on_click=press,
                           args=(value,), use_container_width=True)

    with st.expander("More functions"):
        for row_index, row in enumerate(MORE_BUTTONS):
            columns = st.columns(len(row))
            for column_index, (label, value) in enumerate(row):
                columns[column_index].button(label, key=f"more_btn_{row_index}_{column_index}",
                                             on_click=press, args=(value,), use_container_width=True)

    with st.expander("History"):
        for item in reversed(st.session_state.history[-10:]):
            st.write(item)

with tab2:
    st.subheader("Trigonometric ratios")
    unit = st.radio("Angle unit", ["Degrees", "Radians"], horizontal=True, key="trig_unit")
    theta = st.number_input("θ =", value=30.0, key="trig_theta")
    rad = math.radians(theta) if unit == "Degrees" else theta
    deg = math.degrees(rad)
    st.write(f"θ = {fmt(deg, 8)}° = {fmt(rad, 8)} rad")

    trig_env = build_env("DEG" if unit == "Degrees" else "RAD")
    sin_v, cos_v = trig_env["sin"](theta), trig_env["cos"](theta)

    def ratio(num, den):
        try:
            return fmt(safe_div(num, den))
        except ZeroDivisionError:
            return "undefined"

    ratio_rows = [
        ("sin θ", fmt(sin_v)), ("cos θ", fmt(cos_v)),
        ("tan θ", ratio(sin_v, cos_v)), ("cot θ", ratio(cos_v, sin_v)),
        ("sec θ", ratio(1, cos_v)), ("csc θ", ratio(1, sin_v)),
    ]
    st.table([{"Function": name, "Value": val} for name, val in ratio_rows])

    st.subheader("Inverse trigonometry")
    v = st.number_input("Value v =", value=0.5, key="inv_v")
    inverse = [("atan(v)", math.atan(v))]
    if -1 <= v <= 1:
        inverse = [("asin(v)", math.asin(v)), ("acos(v)", math.acos(v))] + inverse
    else:
        st.caption("asin aur acos sirf -1 se 1 tak ki value ke liye hote hain.")
    st.table([{"Function": name, "Degrees": fmt(math.degrees(ang), 8),
               "Radians": fmt(ang, 8)} for name, ang in inverse])

with tab3:
    fx = st.text_input("f(x) =", value="sin x")
    op = st.radio("Operation",
                  ["Derivative f'(x)", "Second derivative f''(x)", "Definite integral"],
                  key="calc_op")

    calc_env = build_env("RAD")

    def f(v):
        return safe_eval(fx, calc_env, {"x": v, "theta": v})

    def value_of(text):
        return safe_eval(text, calc_env)

    if op == "Definite integral":
        a_text = st.text_input("Lower limit a", value="0")
        b_text = st.text_input("Upper limit b", value="pi")
    else:
        p_text = st.text_input("Point x =", value="pi/4")

    if st.button("Calculate", key="calc_go"):
        try:
            if op == "Definite integral":
                a, b = value_of(a_text), value_of(b_text)
                answer = fmt(integrate(f, a, b), 6, 1e-8)
                st.success(f"Integral from {a_text} to {b_text} = {answer}")
            elif op == "Derivative f'(x)":
                p = value_of(p_text)
                st.success(f"f'({p_text}) = {fmt(derivative(f, p), 6, 1e-8)}")
            else:
                p = value_of(p_text)
                st.success(f"f''({p_text}) = {fmt(second_derivative(f, p), 6, 1e-8)}")
        except Exception:
            st.error("Check the function, point, or integration limits.")

