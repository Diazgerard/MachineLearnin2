import tensorflow as tf
from tensorflow.keras.utils import image_dataset_from_directory
from tensorflow.keras.applications import EfficientNetB5, ResNet50, InceptionV3
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, Rescaling
from tensorflow.keras.models import Sequential
from sklearn.metrics import classification_report
import numpy as np

# ==========================
# 1. Cargar dataset
# ==========================
path = '/kaggle/input/asl-data/asl_alphabet_structured'

train_val_ds = image_dataset_from_directory(
    path,
    validation_split=0.2,  
    subset="training",
    seed=123,
    image_size=(128, 128),
    batch_size=64
)

test_ds = image_dataset_from_directory(
    path,
    validation_split=0.2,  
    subset="validation",
    seed=123,
    image_size=(128, 128),
    batch_size=64,
)

# Dividir train en train (70%) y valid (10%)
val_size = int(0.125 * tf.data.experimental.cardinality(train_val_ds).numpy())
val_ds = train_val_ds.take(val_size)
train_ds = train_val_ds.skip(val_size)

class_names = train_val_ds.class_names
num_classes = len(class_names)


# ==========================
# 2. Función para construir modelos
# ==========================
def build_model(base_model, num_classes):
    model = Sequential([
        Rescaling(1./255),
        base_model,
        GlobalAveragePooling2D(),
        Dropout(0.5),
        Dense(128, activation="relu"),
        Dropout(0.3),
        Dense(num_classes, activation="softmax")
    ])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model

# ==========================
# 3. Función de entrenamiento y evaluación
# ==========================
def train_and_evaluate(model, name, train_ds, val_ds, test_ds, class_names):
    print(f"\nEntrenando {name}...")
    history = model.fit(train_ds, epochs=2, validation_data=val_ds, verbose=1)
    print("Entrenamiento completado.")

    # Evaluación en test
    print(f"\nEvaluando {name} en el conjunto de test...")
    loss, acc = model.evaluate(test_ds, verbose=1)
    print(f"{name} - Test Loss: {loss:.4f} | Test Accuracy: {acc:.4f}")

    # Predicciones
    y_true = []
    y_pred_classes = []

    for x_batch, y_batch in test_ds:
        preds = model.predict(x_batch, verbose=0) 
        y_true.append(y_batch.numpy())
        y_pred_classes.append(np.argmax(preds, axis=1))

    y_true = np.concatenate(y_true, axis=0)
    y_pred_classes = np.concatenate(y_pred_classes, axis=0)

    # Reporte de clasificación
    print(f"\nReporte de clasificación para {name}:\n")
    print(classification_report(y_true, y_pred_classes, target_names=class_names))

    # Guardar modelo
    model.save(f"{name}_gesture_classifier.keras")

# ==========================
# 4. Definir arquitecturas
# ==========================
models_to_test = {
    "EfficientNetB5": EfficientNetB5(weights="imagenet", include_top=False, input_shape=(128,128,3)),
    "ResNet50": ResNet50(weights="imagenet", include_top=False, input_shape=(128,128,3)),
    "InceptionV3": InceptionV3(weights="imagenet", include_top=False, input_shape=(128,128,3))
}
# ==========================
# 5. Entrenar y evaluar
# ==========================
for name, base_model in models_to_test.items():
    model = build_model(base_model, num_classes)
    train_and_evaluate(model, name, train_ds, val_ds, test_ds, class_names)