import streamlit as st
import numpy as np
import json
from PIL import Image
from gtts import gTTS
import pillow_heif
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models

pillow_heif.register_heif_opener()

st.set_page_config(page_title="Doggy AI", page_icon="🐶")

# ---------- BUILD MODEL ----------
def build_model(num_classes):
    base_model = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(224, 224, 3)
    )
    base_model.trainable = False

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation="relu"),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation="softmax")
    ])
    return model

# ---------- LOAD AI ----------
@st.cache_resource
def load_ai():
    with open("model/class_names.json") as f:
        class_names = json.load(f)

    model = build_model(len(class_names))
    
    # Load weights with skip_mismatch to handle any missing layers
    try:
        model.load_weights("model/dog.weights.h5", skip_mismatch=True)
    except Exception as e:
        st.warning(f"Could not load weights: {e}")

    with open("breeds.json") as f:
        breed_db = json.load(f)

    return model, class_names, breed_db

model, class_names, breed_db = load_ai()

# ---------- UI ----------
st.title("🐶 Hundekender AI")
st.write("Tag et billede eller upload et billede af en hund")

tab1, tab2 = st.tabs(["📷 Kamera", "📁 Upload"])  # ← tabs, ikke tab

img = None

with tab1:
    # Vis kamera kun når brugeren eksplicit åbner det
    if "show_camera" not in st.session_state:
        st.session_state.show_camera = False

    if st.button("Åbn kamera"):
        st.session_state.show_camera = True

    if st.session_state.show_camera:
        cam = st.camera_input("Tag et billede")
        if cam:
            img = Image.open(cam).convert("RGB")

        if st.button("Luk kamera"):
            st.session_state.show_camera = False

with tab2:
    up = st.file_uploader("Upload billede", type=["jpg", "jpeg", "png", "heic"])
    if up:
        img = Image.open(up).convert("RGB")

# ---------- PREDICTION ----------
if img:
    st.image(img, caption="Input", use_container_width=True)

    img_resized = img.resize((224, 224))
    x = np.array(img_resized) / 255.0
    x = np.expand_dims(x, axis=0)

    probs = model.predict(x)[0]

    top3_idx = np.argsort(probs)[::-1][:3]
    st.subheader("🔍 Model gæt")

    for i in top3_idx:
        breed = class_names[int(i)].replace("_", " ").title()
        confidence = probs[int(i)]
        st.write(f"**{breed}** — {confidence:.2%}")

    main_breed = class_names[int(top3_idx[0])]
    info = breed_db.get(main_breed)

