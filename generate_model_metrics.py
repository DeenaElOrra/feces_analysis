"""
Geração de Métricas Completas do Modelo
- Curva ROC (multiclass)
- AUC Score
- Matriz de Confusão
- Comparação de todos os modelos
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix,
    roc_curve,
    auc,
    classification_report,
    roc_auc_score
)
from sklearn.preprocessing import label_binarize
import tensorflow as tf
from tensorflow import keras
import os
import glob
from datetime import datetime

# Configurações
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class ModelMetricsGenerator:
    def __init__(self, labels_file='labels_v2_balanced.csv', dataset_dir='dataset'):
        """
        Inicializa o gerador de métricas

        Args:
            labels_file: Arquivo CSV com labels
            dataset_dir: Diretório com imagens
        """
        self.labels_file = labels_file
        self.dataset_dir = dataset_dir
        self.n_classes = 7
        self.class_names = [f'Type {i}' for i in range(1, 8)]

        # Carregar dados
        self.load_data()

    def load_data(self):
        """Carrega e prepara os dados de teste"""
        print("📁 Carregando dados...")

        # Carregar labels
        df = pd.read_csv(self.labels_file)

        # Usar TODO o dataset para avaliação (métricas mais robustas)
        self.test_df = df
        print(f"✅ {len(df)} imagens carregadas para avaliação (100% do dataset)")

    def load_and_preprocess_image(self, image_path):
        """Carrega e preprocessa uma imagem"""
        try:
            img = keras.preprocessing.image.load_img(
                image_path,
                target_size=(224, 224)
            )
            img_array = keras.preprocessing.image.img_to_array(img)
            img_array = img_array / 255.0
            return img_array
        except Exception as e:
            print(f"Erro ao carregar {image_path}: {e}")
            return None

    def get_predictions(self, model, images):
        """Obtém predições do modelo"""
        print("🔮 Gerando predições...")
        predictions = []

        for i, img in enumerate(images):
            if i % 50 == 0:
                print(f"  Processando {i}/{len(images)}...")

            img_batch = np.expand_dims(img, axis=0)
            pred = model.predict(img_batch, verbose=0)
            predictions.append(pred[0])

        return np.array(predictions)

    def plot_confusion_matrix(self, y_true, y_pred, model_name, save_path):
        """Plota matriz de confusão"""
        cm = confusion_matrix(y_true, y_pred)

        plt.figure(figsize=(12, 10))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=self.class_names,
            yticklabels=self.class_names,
            cbar_kws={'label': 'Número de Predições'}
        )
        plt.title(f'Matriz de Confusão - {model_name}\n', fontsize=16, fontweight='bold')
        plt.ylabel('Classe Verdadeira', fontsize=12)
        plt.xlabel('Classe Predita', fontsize=12)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Matriz de confusão salva: {save_path}")
        plt.close()

        # Matriz normalizada
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

        plt.figure(figsize=(12, 10))
        sns.heatmap(
            cm_normalized,
            annot=True,
            fmt='.2%',
            cmap='Blues',
            xticklabels=self.class_names,
            yticklabels=self.class_names,
            cbar_kws={'label': 'Percentual'}
        )
        plt.title(f'Matriz de Confusão Normalizada - {model_name}\n', fontsize=16, fontweight='bold')
        plt.ylabel('Classe Verdadeira', fontsize=12)
        plt.xlabel('Classe Predita', fontsize=12)
        plt.tight_layout()
        save_path_norm = save_path.replace('.png', '_normalized.png')
        plt.savefig(save_path_norm, dpi=300, bbox_inches='tight')
        print(f"✅ Matriz normalizada salva: {save_path_norm}")
        plt.close()

    def plot_roc_curves(self, y_true, y_pred_proba, model_name, save_path):
        """Plota curvas ROC para cada classe"""
        # Binarizar labels
        y_true_bin = label_binarize(y_true, classes=list(range(self.n_classes)))

        # Calcular ROC curve e AUC para cada classe
        fpr = dict()
        tpr = dict()
        roc_auc = dict()

        for i in range(self.n_classes):
            fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_pred_proba[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])

        # ROC micro-average
        fpr["micro"], tpr["micro"], _ = roc_curve(y_true_bin.ravel(), y_pred_proba.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

        # Plotar
        plt.figure(figsize=(14, 10))

        # Micro-average
        plt.plot(
            fpr["micro"], tpr["micro"],
            label=f'Micro-average (AUC = {roc_auc["micro"]:.3f})',
            color='deeppink', linestyle=':', linewidth=3
        )

        # Por classe
        colors = plt.cm.Set1(np.linspace(0, 1, self.n_classes))
        for i, color in zip(range(self.n_classes), colors):
            plt.plot(
                fpr[i], tpr[i],
                color=color,
                lw=2,
                label=f'{self.class_names[i]} (AUC = {roc_auc[i]:.3f})'
            )

        # Linha de referência (classificador aleatório)
        plt.plot([0, 1], [0, 1], 'k--', lw=2, label='Chance (AUC = 0.5)')

        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Taxa de Falsos Positivos (FPR)', fontsize=12)
        plt.ylabel('Taxa de Verdadeiros Positivos (TPR)', fontsize=12)
        plt.title(f'Curvas ROC - {model_name}\n', fontsize=16, fontweight='bold')
        plt.legend(loc="lower right", fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Curvas ROC salvas: {save_path}")
        plt.close()

        return roc_auc

    def plot_auc_scores(self, roc_auc, model_name, save_path):
        """Plota gráfico de barras com AUC scores"""
        classes = self.class_names + ['Micro-Avg']
        scores = [roc_auc[i] for i in range(self.n_classes)] + [roc_auc['micro']]

        plt.figure(figsize=(12, 6))
        bars = plt.bar(classes, scores, color=plt.cm.Set1(np.linspace(0, 1, len(classes))))

        # Adicionar valores nas barras
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}',
                ha='center', va='bottom', fontweight='bold'
            )

        plt.axhline(y=0.5, color='r', linestyle='--', label='Baseline (0.5)')
        plt.ylim([0, 1.1])
        plt.ylabel('AUC Score', fontsize=12)
        plt.xlabel('Classe', fontsize=12)
        plt.title(f'AUC Scores por Classe - {model_name}\n', fontsize=16, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ AUC scores salvos: {save_path}")
        plt.close()

    def generate_metrics_for_model(self, model_path, model_name, output_dir='metrics_output'):
        """Gera todas as métricas para um modelo"""
        print(f"\n{'='*60}")
        print(f"📊 Gerando métricas para: {model_name}")
        print(f"{'='*60}\n")

        # Criar diretório de saída
        os.makedirs(output_dir, exist_ok=True)

        # Carregar modelo
        print(f"🔄 Carregando modelo: {model_path}")
        model = keras.models.load_model(model_path)

        # Preparar dados de teste
        images = []
        labels = []

        for _, row in self.test_df.iterrows():
            img_path = os.path.join(self.dataset_dir, row['filename'])
            if not os.path.exists(img_path):
                # Tentar caminho alternativo
                img_path = row['filename']

            img = self.load_and_preprocess_image(img_path)
            if img is not None:
                images.append(img)
                labels.append(row['bristol_type'] - 1)  # 0-indexed

        images = np.array(images)
        labels = np.array(labels)

        print(f"✅ {len(images)} imagens carregadas para avaliação")

        # Obter predições
        predictions_proba = self.get_predictions(model, images)
        predictions = np.argmax(predictions_proba, axis=1)

        # Calcular acurácia
        accuracy = np.mean(predictions == labels)
        print(f"\n🎯 Acurácia: {accuracy:.4f} ({accuracy*100:.2f}%)")

        # 1. Matriz de Confusão
        cm_path = os.path.join(output_dir, f'{model_name}_confusion_matrix.png')
        self.plot_confusion_matrix(labels, predictions, model_name, cm_path)

        # 2. Curvas ROC
        roc_path = os.path.join(output_dir, f'{model_name}_roc_curves.png')
        roc_auc = self.plot_roc_curves(labels, predictions_proba, model_name, roc_path)

        # 3. AUC Scores
        auc_path = os.path.join(output_dir, f'{model_name}_auc_scores.png')
        self.plot_auc_scores(roc_auc, model_name, auc_path)

        # 4. Classification Report
        report = classification_report(
            labels, predictions,
            target_names=self.class_names,
            digits=4
        )
        print(f"\n📋 Classification Report:\n{report}")

        # Salvar report
        report_path = os.path.join(output_dir, f'{model_name}_classification_report.txt')
        with open(report_path, 'w') as f:
            f.write(f"Model: {model_name}\n")
            f.write(f"Accuracy: {accuracy:.4f}\n\n")
            f.write(f"AUC Scores:\n")
            for i in range(self.n_classes):
                f.write(f"  {self.class_names[i]}: {roc_auc[i]:.4f}\n")
            f.write(f"  Micro-Average: {roc_auc['micro']:.4f}\n\n")
            f.write(report)

        print(f"✅ Report salvo: {report_path}")

        return {
            'model_name': model_name,
            'accuracy': accuracy,
            'auc_micro': roc_auc['micro'],
            'auc_per_class': {self.class_names[i]: roc_auc[i] for i in range(self.n_classes)},
            'predictions': predictions,
            'labels': labels
        }


class ModelComparison:
    """Compara múltiplos modelos"""

    def __init__(self):
        self.models_info = []

    def add_model(self, metrics_dict):
        """Adiciona métricas de um modelo"""
        self.models_info.append(metrics_dict)

    def plot_accuracy_comparison(self, save_path='metrics_output/models_accuracy_comparison.png'):
        """Compara acurácia de todos os modelos"""
        if not self.models_info:
            print("⚠️ Nenhum modelo para comparar")
            return

        model_names = [m['model_name'] for m in self.models_info]
        accuracies = [m['accuracy'] * 100 for m in self.models_info]

        plt.figure(figsize=(14, 8))
        bars = plt.bar(model_names, accuracies, color=plt.cm.viridis(np.linspace(0, 1, len(model_names))))

        # Adicionar valores nas barras
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=11
            )

        plt.ylim([0, 105])
        plt.ylabel('Acurácia (%)', fontsize=13, fontweight='bold')
        plt.xlabel('Modelo', fontsize=13, fontweight='bold')
        plt.title('Comparação de Acurácia Entre Modelos\n', fontsize=16, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Comparação de acurácia salva: {save_path}")
        plt.close()

    def plot_auc_comparison(self, save_path='metrics_output/models_auc_comparison.png'):
        """Compara AUC micro-average de todos os modelos"""
        if not self.models_info:
            print("⚠️ Nenhum modelo para comparar")
            return

        model_names = [m['model_name'] for m in self.models_info]
        auc_scores = [m['auc_micro'] for m in self.models_info]

        plt.figure(figsize=(14, 8))
        bars = plt.bar(model_names, auc_scores, color=plt.cm.plasma(np.linspace(0, 1, len(model_names))))

        # Adicionar valores nas barras
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}',
                ha='center', va='bottom', fontweight='bold', fontsize=11
            )

        plt.axhline(y=0.5, color='r', linestyle='--', label='Baseline (0.5)', linewidth=2)
        plt.ylim([0, 1.1])
        plt.ylabel('AUC Score (Micro-Average)', fontsize=13, fontweight='bold')
        plt.xlabel('Modelo', fontsize=13, fontweight='bold')
        plt.title('Comparação de AUC Score Entre Modelos\n', fontsize=16, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Comparação de AUC salva: {save_path}")
        plt.close()

    def plot_comprehensive_comparison(self, save_path='metrics_output/models_comprehensive_comparison.png'):
        """Comparação abrangente com múltiplas métricas"""
        if not self.models_info:
            print("⚠️ Nenhum modelo para comparar")
            return

        model_names = [m['model_name'] for m in self.models_info]
        accuracies = [m['accuracy'] * 100 for m in self.models_info]
        auc_scores = [m['auc_micro'] * 100 for m in self.models_info]

        x = np.arange(len(model_names))
        width = 0.35

        fig, ax = plt.subplots(figsize=(16, 9))

        bars1 = ax.bar(x - width/2, accuracies, width, label='Acurácia (%)', color='skyblue', edgecolor='black')
        bars2 = ax.bar(x + width/2, auc_scores, width, label='AUC Score (%)', color='lightcoral', edgecolor='black')

        # Adicionar valores
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=9
                )

        ax.set_ylabel('Score (%)', fontsize=13, fontweight='bold')
        ax.set_xlabel('Modelo', fontsize=13, fontweight='bold')
        ax.set_title('Comparação Abrangente: Acurácia vs AUC Score\n', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(model_names, rotation=45, ha='right')
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim([0, 105])

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Comparação abrangente salva: {save_path}")
        plt.close()

    def generate_summary_table(self, save_path='metrics_output/models_summary_table.csv'):
        """Gera tabela resumo com todas as métricas"""
        if not self.models_info:
            print("⚠️ Nenhum modelo para comparar")
            return

        data = []
        for model in self.models_info:
            row = {
                'Modelo': model['model_name'],
                'Acurácia (%)': f"{model['accuracy']*100:.2f}",
                'AUC Micro': f"{model['auc_micro']:.4f}"
            }
            # Adicionar AUC por classe
            for class_name, auc_val in model['auc_per_class'].items():
                row[f'AUC {class_name}'] = f"{auc_val:.4f}"

            data.append(row)

        df = pd.DataFrame(data)
        df.to_csv(save_path, index=False)
        print(f"✅ Tabela resumo salva: {save_path}")
        print(f"\n{df.to_string(index=False)}\n")


def main():
    """Função principal"""
    print("="*80)
    print("🚀 GERADOR DE MÉTRICAS COMPLETAS - FLORA APP")
    print("="*80)
    print()

    # Inicializar gerador
    generator = ModelMetricsGenerator()
    comparison = ModelComparison()

    # Encontrar todos os modelos .h5
    model_files = {
        'Modelo V1 (Original)': 'best_model_fe.h5',
        'Modelo V2 (Balanceado)': 'best_model_fe_balanced.h5',
        'Modelo V2 (Desbalanceado)': 'best_model_fe_V2.h5',
        'Modelo Augmented': 'best_model_fe_AUGMENTED.h5',
    }

    # Verificar quais modelos existem
    available_models = {}
    for name, path in model_files.items():
        if os.path.exists(path):
            available_models[name] = path
        else:
            print(f"⚠️ Modelo não encontrado: {path}")

    if not available_models:
        print("❌ Nenhum modelo encontrado!")
        print("\nModelos esperados:")
        for name, path in model_files.items():
            print(f"  - {path}")
        return

    print(f"\n✅ {len(available_models)} modelo(s) encontrado(s):\n")
    for name in available_models:
        print(f"  • {name}")
    print()

    # Gerar métricas para cada modelo
    for model_name, model_path in available_models.items():
        try:
            metrics = generator.generate_metrics_for_model(model_path, model_name)
            comparison.add_model(metrics)
        except Exception as e:
            print(f"\n❌ Erro ao processar {model_name}: {e}\n")

    # Gerar comparações
    print(f"\n{'='*60}")
    print("📊 GERANDO COMPARAÇÕES ENTRE MODELOS")
    print(f"{'='*60}\n")

    comparison.plot_accuracy_comparison()
    comparison.plot_auc_comparison()
    comparison.plot_comprehensive_comparison()
    comparison.generate_summary_table()

    print(f"\n{'='*80}")
    print("✅ PROCESSO CONCLUÍDO!")
    print(f"{'='*80}")
    print(f"\n📁 Todos os resultados foram salvos em: metrics_output/\n")


if __name__ == "__main__":
    main()
