import streamlit as st
import pandas as pd
import random
import time

# Updated kitchen affirmations
affirmations = [
    "You're going to have a great event today!",
    "September is coming. Rest is near!",
    "You're doing great work, keep pushing.",
    "Big events start with small prep wins.",
    "Your mise en place is your superpower.",
    "Stay sharp. Stay strong. Stay caffeinated ☕️.",
    "Organization is the secret ingredient.",
    "The guests won't know, but your team will. Great work!",
    "Good prep saves lives (and lunch rushes).",
    "Every tray you prep is a step closer to success.",
    "Take pride in every tray, every plate, every garnish.",
    "Today's prep is tomorrow's peace.",
    "Keep those knives sharp and your spirits sharper."
]

def scale_recipe(recipe_df, number_of_guests):
    base_servings = recipe_df["BaseServings"].iloc[0]
    scale_factor = number_of_guests / base_servings
    recipe_df["ScaledQuantity"] = recipe_df["Quantity"] * scale_factor
    return recipe_df

def format_shopping_list(scaled_df):
    shopping_list = ""
    grouped = scaled_df.groupby(["Category"])
    for category, group in grouped:
        shopping_list += f"\n**Ingredients - {category}:**\n"
        for _, row in group.sort_values("Ingredient").iterrows():
            purchase_format = row.get("PurchaseFormat", "")
            quantity = row["ScaledQuantity"]
            ingredient = row["Ingredient"]
            note = row.get("Note", "")
            unit = row["Unit"]
            if pd.isna(purchase_format) or purchase_format == "":
                if unit == "pcs":
                    purchase_format = "each"
                elif category.lower() in ["herbs", "greens", "lettuce", "parsley", "cilantro", "dill", "spinach"]:
                    purchase_format = "bunch"
                elif category.lower() in ["carrots", "celery", "onions"]:
                    purchase_format = "bag"
                else:
                    purchase_format = ""
            if purchase_format:
                shopping_list += f"- {int(quantity)} {purchase_format} {ingredient}"
            else:
                shopping_list += f"- {quantity:.2f} {unit} {ingredient}"
            if pd.notna(note) and note != "":
                shopping_list += f" | Note: {note}"
            shopping_list += "\n"
    return shopping_list

def create_download_link(content, filename, label):
    import base64
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">{label}</a>'

# Streamlit App Configuration
st.set_page_config(page_title="Catering Companion", page_icon="🍴", layout="centered")

# Custom dark background CSS with utensils pattern
st.markdown(
    """
    <style>
    body {
        background-color: #1e1e1e;
        background-image: url('https://www.transparenttextures.com/patterns/chefskitchen.png');
        background-size: 300px;
        background-repeat: repeat;
        color: white;
    }
    textarea, input, .stTextInput>div>div>input {
        background-color: #333333;
        color: white;
    }
    .css-1d391kg {padding-top: 2rem;}
    .reportview-container {background: #1e1e1e; color: white;}
    #MainMenu, header, footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🍴 Catering Companion")

uploaded_file = st.file_uploader("Upload your Master Recipes CSV", type=["csv"])

if uploaded_file:
    recipes_df = pd.read_csv(uploaded_file)
    available_recipes = recipes_df["RecipeName"].unique()

    user_input = st.text_input("Type your request (e.g., Meatballs, Caesar Salad for 300 people):")

    if st.button("Generate Plan"):
        if user_input.strip() != "":
            st.write("✨ " + random.choice(affirmations))
            with st.spinner('Thinking...'):
                time.sleep(2)  # Simulate thinking time

                # Parse user input
                input_lower = user_input.lower()
                guest_number = 10  # default
                for word in input_lower.split():
                    if word.isdigit():
                        guest_number = int(word)

                selected_recipes = []
                for recipe in available_recipes:
                    if recipe.lower() in input_lower:
                        selected_recipes.append(recipe)

                if not selected_recipes:
                    st.warning("No matching recipes found. Please check spelling or add recipes to your master list.")
                else:
                    combined_scaled = pd.DataFrame()
                    methods = {}

                    for recipe_name in selected_recipes:
                        recipe_data = recipes_df[recipes_df["RecipeName"] == recipe_name]
                        scaled_recipe = scale_recipe(recipe_data, guest_number)
                        combined_scaled = pd.concat([combined_scaled, scaled_recipe], ignore_index=True)
                        methods[recipe_name] = recipe_data["Method"].iloc[0]

                    combined_scaled = combined_scaled.groupby(
                        ["Ingredient", "Unit", "Category", "Note", "PurchaseFormat"], as_index=False
                    ).sum()

                    shopping_list = format_shopping_list(combined_scaled)

                    st.markdown("# 🛒 Combined Shopping List")
                    st.markdown(shopping_list)

                    st.markdown("---")
                    st.markdown("# 📃 Recipe Methods")
                    methods_text = ""
                    for recipe_name, method in methods.items():
                        st.markdown(f"## {recipe_name}")
                        st.markdown(method)
                        st.markdown('<div style="page-break-after: always;"></div>', unsafe_allow_html=True)
                        methods_text += f"{recipe_name}\n{method}\n\n"

                    st.markdown(create_download_link(shopping_list, "shopping_list.txt", "📥 Download Shopping List (.txt)"), unsafe_allow_html=True)
                    st.markdown(create_download_link(methods_text, "recipe_methods.txt", "📥 Download Recipe Methods (.txt)"), unsafe_allow_html=True)
else:
    st.info("Upload a CSV file to get started. Your file should include: RecipeName, BaseServings, Ingredient, Quantity, Unit, Category, Note, PurchaseFormat, Method.")
