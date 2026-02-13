"""
Train secondary classifier (Agent B) for fine-grained material verification.

10 classes: battery, biological, cardboard, clothes, glass, metal, paper, plastic, shoes, trash

Usage:
    python train_classifier.py --data "../garbage classification/standardized_256" --epochs 30
"""

import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from pathlib import Path
import time


def create_model(num_classes=10, pretrained=True):
    """Create EfficientNet-B0 model for classification."""
    model = models.efficientnet_b0(pretrained=pretrained)
    # Replace final layer
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    return model


def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    for inputs, labels in loader:
        inputs, labels = inputs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
    
    return running_loss / len(loader), 100. * correct / total


def validate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for inputs, labels in loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
    
    return running_loss / len(loader), 100. * correct / total


def main():
    parser = argparse.ArgumentParser(description="Train secondary classifier")
    parser.add_argument("--data", required=True, help="Path to data folder with class subfolders")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda", "0", "1"])
    parser.add_argument("--output", default="../models/classifier_tier2.pt")
    args = parser.parse_args()
    
    # Setup device
    device = torch.device("cuda" if args.device in ["cuda", "0", "1"] and torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Data transforms
    train_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # Load data
    data_path = Path(args.data)
    print(f"\nLoading data from: {data_path}")
    
    # Create dataset (assumes all images in class folders, we'll split 80/20)
    full_dataset = datasets.ImageFolder(data_path, transform=train_transform)
    
    # Split train/val
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        full_dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    # Update val dataset transform
    val_dataset.dataset.transform = val_transform
    
    print(f"Train samples: {len(train_dataset)}")
    print(f"Val samples: {len(val_dataset)}")
    print(f"Classes: {full_dataset.classes}")
    
    # DataLoaders
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)
    
    # Model
    num_classes = len(full_dataset.classes)
    model = create_model(num_classes=num_classes, pretrained=True).to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)
    
    # Training loop
    best_val_acc = 0.0
    print(f"\n{'='*60}")
    print(f"Training Secondary Classifier (Agent B)")
    print(f"{'='*60}\n")
    
    for epoch in range(args.epochs):
        start = time.time()
        
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        
        scheduler.step(val_loss)
        
        elapsed = time.time() - start
        
        print(f"Epoch {epoch+1}/{args.epochs} ({elapsed:.1f}s) - "
              f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% - "
              f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'classes': full_dataset.classes,
            }, output_path)
            print(f"  ✓ Saved best model (Val Acc: {val_acc:.2f}%)")
    
    print(f"\n{'='*60}")
    print(f"✅ Training Complete!")
    print(f"Best validation accuracy: {best_val_acc:.2f}%")
    print(f"Model saved to: {args.output}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
