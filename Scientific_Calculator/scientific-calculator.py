
import math
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

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

    sin_ = lambda x: math.sin(to_rad(x))
    cos_ = lambda x: math.cos(to_rad(x))

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
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "asinh": math.asinh,
        "acosh": math.acosh,
        "atanh": math.atanh,
        "log": math.log10,
        "ln": math.log,
        "sqrt": math.sqrt,
        "exp": math.exp,
        "fact": math.factorial,
        "abs": abs,
        "pow": math.pow,
        "floor": math.floor,
        "ceil": math.ceil,
        "radians": math.radians,
        "degrees": math.degrees,
        "pi": math.pi,
        "e": math.e,
    }


def safe_eval(text, env, extra=None):
    if "__" in text:
        raise ValueError("not allowed")

    text = (
        text.replace("^", "**")
        .replace("×", "*")
        .replace("÷", "/")
        .replace("π", "pi")
        .replace("θ", "theta")
    )

    text = text.strip()

    if not text:
        raise ValueError("Empty expression")

    if text.count("(") > text.count(")"):
        text += ")" * (text.count("(") - text.count(")"))

    scope = {"__builtins__": {}, **env}

    if extra:
        scope.update(extra)

    result = eval(text, scope)

    if isinstance(result, complex):
        raise ValueError("complex result")

    return result


def fmt(value, digits=10, tol=1e-12):
    if abs(value) < tol:
        return "0"
    return f"{value:.{digits}g}"


def derivative(f, x, h=1e-3):
    return (
        -f(x + 2 * h)
        + 8 * f(x + h)
        - 8 * f(x - h)
        + f(x - 2 * h)
    ) / (12 * h)


def second_derivative(f, x, h=1e-3):
    return (f(x + h) - 2 * f(x) + f(x - h)) / h**2


def integrate(f, a, b, n=2000):
    h = (b - a) / n
    total = f(a) + f(b)

    for i in range(1, n):
        total += (4 if i % 2 else 2) * f(a + i * h)

    return total * h / 3


st.set_page_config(
    page_title="Scientific Calculator",
    page_icon="🧮",
    layout="wide"
)

defaults = {
    "expr": "",
    "result": "",
    "history": [],
    "mode": "DEG"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def calculate():
    s = st.session_state

    if not s.expr.strip():
        return

    try:
        value = safe_eval(s.expr, build_env(s.mode))
        s.result = fmt(value)
        s.history.append(f"{s.expr} = {s.result}")

    except ZeroDivisionError:
        s.result = "Error: undefined / zero se divide"

    except Exception:
        s.result = "Error: expression sahi nahi"


def press(key):
    s = st.session_state

    if key == "C":
        s.expr = ""
        s.result = ""

    elif key == "DEL":
        s.expr = s.expr[:-1]
        s.result = ""

    elif key == "=":
        calculate()

    elif key == "ANS":
        if s.result and not s.result.startswith("Error"):
            s.expr += s.result

    elif key in {
        "sin", "cos", "tan", "cot", "sec", "csc",
        "asin", "acos", "atan", "acot",
        "sinh", "cosh", "tanh", "log", "ln",
        "sqrt", "fact", "abs", "exp"
    }:
        s.expr += key + "("
        s.result = ""

    else:
        s.expr += key
        s.result = ""


st.title("🧮 Scientific Calculator")

tab1, tab2, tab3, tab4 = st.tabs([
    "Calculator",
    "Trigonometry",
    "Calculus",
    "Web Calculator",
])

with tab1:
    st.radio(
        "Angle mode",
        ["DEG", "RAD"],
        horizontal=True,
        key="mode"
    )

    st.text_input(
        "Enter your expression",
        key="expr",
        on_change=calculate,
        placeholder="Example: cos(30 or 5 + 10"
    )

    st.markdown(f"### Result: {st.session_state.result or '—'}")

    button_rows = [
        ["sin", "cos", "tan", "cot", "sec"],
        ["csc", "asin", "acos", "atan", "acot"],
        ["sinh", "cosh", "tanh", "log", "ln"],
        ["sqrt", "^", "pi", "e", "fact"],
        ["(", ")", "%", "DEL", "C"],
        ["7", "8", "9", "/", "ANS"],
        ["4", "5", "6", "*", "-"],
        ["1", "2", "3", "+", "="],
        ["0", ".", ",", "abs", "exp"]
    ]

    for r, row in enumerate(button_rows):
        cols = st.columns(len(row))

        for c, label in enumerate(row):
            cols[c].button(
                label,
                key=f"btn_{r}_{c}",
                on_click=press,
                args=(label,),
                use_container_width=True
            )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Clear All", use_container_width=True):
            st.session_state.expr = ""
            st.session_state.result = ""

    with col2:
        if st.button("Clear History", use_container_width=True):
            st.session_state.history = []

    with st.expander("Calculation History"):
        for item in reversed(st.session_state.history[-10:]):
            st.write(item)


with tab2:
    st.subheader("Trigonometric Ratios")

    unit = st.radio(
        "Angle unit",
        ["Degrees", "Radians"],
        horizontal=True,
        key="trig_unit"
    )

    theta = st.number_input(
        "Enter angle θ",
        value=30.0,
        key="trig_theta"
    )

    rad = math.radians(theta) if unit == "Degrees" else theta
    deg = math.degrees(rad)

    st.write(f"θ = {fmt(deg, 8)}° = {fmt(rad, 8)} rad")

    sin_v = math.sin(rad)
    cos_v = math.cos(rad)

    def ratio(num, den):
        try:
            return fmt(safe_div(num, den))
        except ZeroDivisionError:
            return "undefined"

    ratio_rows = [
        ("sin θ", fmt(sin_v)),
        ("cos θ", fmt(cos_v)),
        ("tan θ", ratio(sin_v, cos_v)),
        ("cot θ", ratio(cos_v, sin_v)),
        ("sec θ", ratio(1, cos_v)),
        ("csc θ", ratio(1, sin_v))
    ]

    st.table([
        {"Function": name, "Value": value}
        for name, value in ratio_rows
    ])

    st.subheader("Inverse Trigonometry")

    v = st.number_input(
        "Enter value",
        value=0.5,
        key="inv_v"
    )

    inverse = [("atan(v)", math.atan(v))]

    if -1 <= v <= 1:
        inverse = [
            ("asin(v)", math.asin(v)),
            ("acos(v)", math.acos(v))
        ] + inverse
    else:
        st.caption("asin aur acos ke liye value -1 se 1 tak honi chahiye.")

    st.table([
        {
            "Function": name,
            "Degrees": fmt(math.degrees(ang), 8),
            "Radians": fmt(ang, 8)
        }
        for name, ang in inverse
    ])


with tab3:
    st.write(
        "Variable x ya theta use karein. "
        "Calculus radians mein calculate hota hai. "
        "Examples: sin(x), cos(theta)**2, x*tan(x)."
    )

    fx = st.text_input("f(x)", value="sin(x)", key="fx")

    op = st.radio(
        "Select operation",
        [
            "Derivative f'(x)",
            "Second derivative f''(x)",
            "Definite integral"
        ],
        key="calc_op"
    )

    calc_env = build_env("RAD")

    def f(v):
        return safe_eval(fx, calc_env, {"x": v, "theta": v})

    def value_of(text):
        return safe_eval(text, calc_env)

    if op == "Definite integral":
        a_text = st.text_input("Lower limit a", value="0")
        b_text = st.text_input("Upper limit b", value="pi")
    else:
        p_text = st.text_input("Point x", value="pi/4")

    if st.button("Calculate", key="calc_go"):
        try:
            if op == "Definite integral":
                a = value_of(a_text)
                b = value_of(b_text)
                answer = fmt(integrate(f, a, b), 6, 1e-8)

                st.success(
                    f"Integral from {a_text} to {b_text} = {answer}"
                )

            elif op == "Derivative f'(x)":
                p = value_of(p_text)
                st.success(
                    f"f'({p_text}) = {fmt(derivative(f, p), 6, 1e-8)}"
                )

            else:
                p = value_of(p_text)
                st.success(
                    f"f''({p_text}) = {fmt(second_derivative(f, p), 6, 1e-8)}"
                )

        except Exception:
            st.error(
                "Expression, point ya limits check karein. "
                "Function wahan defined nahi ho sakta."
            )

with tab4:
    calculator_html = Path(__file__).with_name("calculator.html").read_text(encoding="utf-8")
    components.html(calculator_html, height=1100, scrolling=True)
