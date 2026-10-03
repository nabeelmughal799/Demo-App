import math
import streamlit as st

st.set_page_config(page_title="Scientific Calculator", page_icon="🧮")

# ---------- 1. SESSION STATE ----------
# Streamlit har click par poora code dobara chalata hai.
# Isliye expression, result aur history ko session_state me save karte hain.
if "expr" not in st.session_state:
    st.session_state.expr = ""
if "result" not in st.session_state:
    st.session_state.result = ""
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- 2. ANGLE MODE (DEG / RAD) ----------
mode = st.radio("Angle mode", ["DEG", "RAD"], horizontal=True)

def build_env(mode):
    """Dictionary jisme har allowed function ka naam aur uska asli function hai."""
    if mode == "DEG":
        sin = lambda x: math.sin(math.radians(x))
        cos = lambda x: math.cos(math.radians(x))
        tan = lambda x: math.tan(math.radians(x))
        asin = lambda x: math.degrees(math.asin(x))
        acos = lambda x: math.degrees(math.acos(x))
        atan = lambda x: math.degrees(math.atan(x))
    else:
        sin, cos, tan = math.sin, math.cos, math.tan
        asin, acos, atan = math.asin, math.acos, math.atan
    return {
        "sin": sin, "cos": cos, "tan": tan,
        "asin": asin, "acos": acos, "atan": atan,
        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
        "log": math.log10, "ln": math.log, "sqrt": math.sqrt,
        "exp": math.exp, "fact": math.factorial, "abs": abs,
        "floor": math.floor, "ceil": math.ceil, "pow": math.pow,
        "pi": math.pi, "e": math.e,
    }

ENV = build_env(mode)

# ---------- 3. EVALUATE ----------
def safe_eval(text, extra=None):
    """Text ko calculate karta hai, sirf ENV ke functions allowed hain."""
    text = text.replace("^", "**").replace("×", "*").replace("÷", "/")
    scope = {"__builtins__": {}, **ENV}
    if extra:
        scope.update(extra)
    return eval(text, scope)

def calculate():
    s = st.session_state
    try:
        value = safe_eval(s.expr)
        s.result = f"{value:.10g}"
        s.history.append(f"{s.expr} = {s.result}")
    except ZeroDivisionError:
        s.result = "Error: zero se divide nahi hota"
    except Exception:
        s.result = "Error: expression sahi nahi"

# ---------- 4. BUTTON PRESS ----------
def press(key):
    s = st.session_state
    if key == "C":
        s.expr, s.result = "", ""
    elif key == "DEL":
        s.expr = s.expr[:-1]
    elif key == "=":
        calculate()
    elif key == "ANS":
        s.expr += s.result
    else:
        s.expr += key

# ---------- 5. CALCULUS (numerical) ----------
def derivative(f, x, h=1e-3):
    # 5-point formula: kaafi accurate hota hai
    return (-f(x + 2*h) + 8*f(x + h) - 8*f(x - h) + f(x - 2*h)) / (12 * h)

def integrate(f, a, b, n=2000):
    # Simpson's rule (n hamesha even hona chahiye)
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):          # loop
        total += (4 if i % 2 else 2) * f(a + i * h)
    return total * h / 3

# ---------- 6. UI ----------
st.title("🧮 Scientific Calculator")
tab1, tab2 = st.tabs(["Calculator", "Calculus"])

with tab1:
    # Keyboard se type karo, Enter dabao -> calculate
    st.text_input("Expression (keyboard se likhein ya buttons dabayein)",
                  key="expr", on_change=calculate)
    st.markdown(f"### = {st.session_state.result}")

    # Buttons ki list of lists (rows)
    rows = [
        ["sin(", "cos(", "tan(", "log(", "ln("],
        ["asin(", "acos(", "atan(", "sqrt(", "^"],
        ["(", ")", "pi", "e", "fact("],
        ["7", "8", "9", "/", "DEL"],
        ["4", "5", "6", "*", "C"],
        ["1", "2", "3", "-", "ANS"],
        ["0", ".", "%", "+", "="],
    ]
    for r, row in enumerate(rows):
        cols = st.columns(len(row))
        for c, key in enumerate(row):
            cols[c].button(key, key=f"btn_{r}_{c}",
                           on_click=press, args=(key,),
                           use_container_width=True)

    with st.expander("History"):
        for item in reversed(st.session_state.history[-10:]):
            st.write(item)

with tab2:
    st.write("Function me variable **x** use karein. Example: `x**2 + sin(x)`")
    fx = st.text_input("f(x) =", value="x**2")
    op = st.radio("Kya karna hai?", ["Derivative", "Integral"], horizontal=True)

    def f(x):
        return safe_eval(fx, {"x": x})

    try:
        if op == "Derivative":
            point = st.number_input("Point x =", value=1.0)
            if st.button("Calculate", key="calc_d"):
                st.success(f"f'({point}) = {derivative(f, point):.6g}")
        else:
            a = st.number_input("Lower limit a", value=0.0)
            b = st.number_input("Upper limit b", value=1.0)
            if st.button("Calculate", key="calc_i"):
                st.success(f"Integral = {integrate(f, a, b):.6g}")
    except Exception:
        st.error("f(x) sahi nahi hai ya is point par defined nahi hai")