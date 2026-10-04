import math
import streamlit as st

# ================= PART 1: MATH (Streamlit ke baghair) =================

def safe_div(num, den):
    """Agar den (neeche wali value) lagbhag 0 ho to 'undefined' error do."""
    if abs(den) < 1e-12:
        raise ZeroDivisionError("undefined")
    return num / den


def build_env(mode):
    """Dictionary: function ka naam -> asli function. mode = 'DEG' ya 'RAD'."""
    if mode == "DEG":
        to_rad = math.radians      # sin/cos/tan ko radians chahiye
        from_rad = math.degrees    # inverse functions ka jawab degrees me
    else:
        to_rad = lambda x: x
        from_rad = lambda x: x

    sin_ = lambda x: math.sin(to_rad(x))
    cos_ = lambda x: math.cos(to_rad(x))

    return {
        # trigonometry
        "sin": sin_,
        "cos": cos_,
        "tan": lambda x: safe_div(sin_(x), cos_(x)),
        "cot": lambda x: safe_div(cos_(x), sin_(x)),
        "sec": lambda x: safe_div(1, cos_(x)),
        "csc": lambda x: safe_div(1, sin_(x)),
        # inverse trigonometry
        "asin": lambda x: from_rad(math.asin(x)),
        "acos": lambda x: from_rad(math.acos(x)),
        "atan": lambda x: from_rad(math.atan(x)),
        "acot": lambda x: from_rad(math.atan2(1, x)),
        # hyperbolic
        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
        "asinh": math.asinh, "acosh": math.acosh, "atanh": math.atanh,
        # baqi functions
        "log": math.log10, "ln": math.log, "sqrt": math.sqrt,
        "exp": math.exp, "fact": math.factorial, "abs": abs,
        "pow": math.pow, "floor": math.floor, "ceil": math.ceil,
        "radians": math.radians, "degrees": math.degrees,
        # constants
        "pi": math.pi, "e": math.e,
    }


def safe_eval(text, env, extra=None):
    """Text ko calculate karo; sirf env ke functions allowed hain."""
    if "__" in text:
        raise ValueError("not allowed")
    text = (text.replace("^", "**").replace("×", "*").replace("÷", "/")
                .replace("π", "pi").replace("θ", "theta"))
    scope = {"__builtins__": {}, **env}
    if extra:
        scope.update(extra)
    result = eval(text, scope)
    if isinstance(result, complex):
        raise ValueError("complex result")
    return result


def fmt(value, digits=10, tol=1e-12):
    """Bohat chhoti value (1e-16 jaisi) ko 0 dikhao, baqi ko saaf format me."""
    if abs(value) < tol:
        return "0"
    return f"{value:.{digits}g}"


def derivative(f, x, h=1e-3):
    """Pehla derivative: 5-point formula."""
    return (-f(x + 2*h) + 8*f(x + h) - 8*f(x - h) + f(x - 2*h)) / (12 * h)


def second_derivative(f, x, h=1e-3):
    """Doosra derivative: central difference."""
    return (f(x + h) - 2 * f(x) + f(x - h)) / h**2


def integrate(f, a, b, n=2000):
    """Definite integral: Simpson's rule (n hamesha even)."""
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += (4 if i % 2 else 2) * f(a + i * h)
    return total * h / 3


# ================= PART 2: STREAMLIT (GUI) =================

st.set_page_config(page_title="Scientific Calculator", page_icon="🧮")

# Session state: values yaad rakhne ke liye
defaults = {"expr": "", "result": "", "history": []}
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
        s.expr, s.result = "", ""
    elif key == "DEL":
        s.expr = s.expr[:-1]
    elif key == "=":
        calculate()
    elif key == "ANS":
        s.expr += s.result
    else:
        s.expr += key


st.title("🧮 Scientific Calculator")
tab1, tab2, tab3 = st.tabs(["Calculator", "Trigonometry", "Calculus"])

# ---------- TAB 1: CALCULATOR ----------
with tab1:
    st.radio("Angle mode", ["DEG", "RAD"], horizontal=True, key="mode")
    st.text_input("Expression (keyboard se likhein, Enter dabayein, ya buttons use karein)",
                  key="expr", on_change=calculate)
    st.markdown(f"### = {st.session_state.result}")

    button_rows = [
        ["sin(", "cos(", "tan(", "cot(", "sec("],
        ["csc(", "asin(", "acos(", "atan(", "acot("],
        ["sinh(", "cosh(", "tanh(", "log(", "ln("],
        ["sqrt(", "^", "pi", "e", "fact("],
        ["(", ")", "%", "DEL", "C"],
        ["7", "8", "9", "/", "ANS"],
        ["4", "5", "6", "*", "-"],
        ["1", "2", "3", "+", "="],
        ["0", ".", ",", "abs(", "exp("],
    ]
    for r, row in enumerate(button_rows):
        cols = st.columns(len(row))
        for c, label in enumerate(row):
            cols[c].button(label, key=f"btn_{r}_{c}", on_click=press,
                           args=(label,), use_container_width=True)

    with st.expander("History"):
        for item in reversed(st.session_state.history[-10:]):
            st.write(item)

# ---------- TAB 2: TRIGONOMETRY ----------
with tab2:
    st.subheader("Trigonometric ratios")
    unit = st.radio("Angle unit", ["Degrees", "Radians"], horizontal=True, key="trig_unit")
    theta = st.number_input("θ =", value=30.0, key="trig_theta")
    rad = math.radians(theta) if unit == "Degrees" else theta
    deg = math.degrees(rad)
    st.write(f"θ = {fmt(deg, 8)}° = {fmt(rad, 8)} rad")

    sin_v, cos_v = math.sin(rad), math.cos(rad)

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

# ---------- TAB 3: CALCULUS ----------
with tab3:
    st.write("Variable **x** ya **theta** use karein. Calculus hamesha radians me hota hai. "
             "Examples: `sin(x)`, `cos(theta)**2`, `x*tan(x)`. π ke liye `pi` likhein.")
    fx = st.text_input("f(x) =", value="sin(x)")
    op = st.radio("Kya karna hai?",
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
            st.error("f(x) ya point/limits sahi nahi hain, ya function wahan defined nahi hai.")