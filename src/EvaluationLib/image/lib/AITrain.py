import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import torch.optim.lr_scheduler as lr_scheduler
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from torchvision.models import resnet50, resnet18

class MyNeuralNetwork(nn.Module):
    def __init__(self,n_classes):
        
        super().__init__()
        #240*240
        self.conv1 = nn.Conv2d(3,12,5)
        self.pool1 = nn.MaxPool2d(5,2) 
        self.conv2 = nn.Conv2d(12,24,7) 
        self.pool2 = nn.MaxPool2d(4,2) 
        self.conv3 = nn.Conv2d(24,48,7) 
        self.pool3 = nn.MaxPool2d(6,2) 
        self.fc2 = nn.Linear(23232,1000)
        self.fc3 = nn.Linear(1000,75)
        self.fc4 = nn.Linear(75,n_classes)

    def forward(self,x):
        #convo rồi relu rồi pool liên tục 3 lớp
        x = self.pool1(F.relu(self.conv1(x)))
        x = self.pool2(F.relu(self.conv2(x)))
        x = self.pool3(F.relu(self.conv3(x)))
        #flatten hình
        x = torch.flatten(x,1)
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x


class AITrain:
    def load_class_structure(folderPath):#Folder structure: Dataset/Classes/Images

        #Normalize the images
        transform = transforms.Compose([
            transforms.Grayscale(3),
            transforms.Resize((224,224)),
            transforms.ToTensor(), 
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        #Load Full Dataset
        full_dataset = torchvision.datasets.ImageFolder(root=folderPath, transform=transform)

        #Split train_test
        dataset_size = len(full_dataset)
        train_size = int(0.7 * dataset_size)
        val_size = int(0.15 * dataset_size)
        test_size = dataset_size - train_size - val_size

        train_dataset, val_dataset, test_dataset = torch.utils.data.random_split(
            full_dataset, 
            [train_size, val_size, test_size],
            generator=torch.Generator().manual_seed(42)  # Đặt seed để tái tạo kết quả
        )

        train_loader = torch.utils.data.DataLoader(train_dataset, 64, shuffle=True)
        val_loader = torch.utils.data.DataLoader(val_dataset, 64, shuffle=True)
        test_loader = torch.utils.data.DataLoader(test_dataset, 64, shuffle=True)


        return {"train_loader": train_loader,"val_loader": val_loader,"test_loader": test_loader}


    def load_folder_structure(folderPath):#Folder structure: Dataset/(Train/Val/Test) Classes/Images
        
        transform = transforms.Compose([
            transforms.Grayscale(3),
            transforms.Resize((224,224)),
            transforms.ToTensor(), 
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        #Load Full Dataset
        train_dataset = torchvision.datasets.ImageFolder(root=f"{folderPath}/train", transform=transform)
        val_dataset = torchvision.datasets.ImageFolder(root=f"{folderPath}/valid", transform=transform)
        test_dataset = torchvision.datasets.ImageFolder(root=f"{folderPath}/test", transform=transform)


        train_loader = torch.utils.data.DataLoader(train_dataset, 64, shuffle=True)
        val_loader = torch.utils.data.DataLoader(val_dataset, 64, shuffle=True)
        test_loader = torch.utils.data.DataLoader(test_dataset, 64, shuffle=True)

        return {"train_loader": train_loader,"val_loader": val_loader,"test_loader": test_loader}
    

    def NNtrain(loader,save_name,epochs,n_classes): #{"train_loader": train_loader,"val_loader": val_loader,"test_loader": test_loader}

        #If device supports cuda then cuda
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f'Device using: {device}')

        model = MyNeuralNetwork(n_classes).to(device)

        #Defining loss criterion, optimizer, scheduler
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.SGD(model.parameters(), lr=0.01,momentum=0.9,weight_decay=1e-5)
        scheduler = lr_scheduler.LinearLR(optimizer, start_factor=1.0, end_factor=0.01, total_iters=epochs)

        #Tracker
        history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
        best_val_acc = 0

        for epoch in range(epochs): 
            # --- Training Phase ---
            model.train()
            running_loss = 0.0
            correct = 0
            total = 0
            
            for images, labels in loader['train_loader']:
                images, labels = images.to(device), labels.to(device)
                
                # Forward pass
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                # Backward và optimize
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                # Tính accuracy
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                running_loss += loss.item() * images.size(0)
            
            before_lr = optimizer.param_groups[0]["lr"]
            scheduler.step()
            after_lr = optimizer.param_groups[0]["lr"]
            print("Epoch %d: SGD lr %.4f -> %.4f" % (epoch, before_lr, after_lr))
            
            train_loss = running_loss / len(loader['train_loader'])
            train_acc = correct / total
            history['train_loss'].append(train_loss)
            history['train_acc'].append(train_acc)
            
            # --- Validation Phase ---
            model.eval()
            val_loss = 0.0
            correct = 0
            total = 0
            
            with torch.no_grad():
                for images, labels in loader['val_loader']:
                    images, labels = images.to(device), labels.to(device)
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                    
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()
                    val_loss += loss.item() * images.size(0)
            
            val_loss = val_loss / len(loader['val_loader'])
            val_acc = correct / total
            history['val_loss'].append(val_loss)
            history['val_acc'].append(val_acc)
            
            #Preventing Overfitting
            if(train_acc>0.85 and train_acc-val_acc>0.1):
                break

            #Saving Best models
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save(model.state_dict(), f'{save_name}.pth')
            
            #Result
            print(f'Epoch [{epoch+1}/20], '
                f'Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, '
                f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}')

        print(f'Best Validation Accuracy: {best_val_acc:.4f}')

    def NNTest(modelName,fileName,classes):
        model = MyNeuralNetwork(len(classes))
        model.load_state_dict(torch.load(modelName))
        model.eval()
        image = Image.open(fileName)
        transform = transforms.Compose([
            transforms.Grayscale(3),
            transforms.Resize((224,224)),
            transforms.ToTensor(), 
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        tensor = transform(image)
        batch = tensor.unsqueeze(0)

        with torch.no_grad():
            output = model(batch)
            _, predicted = torch.max(output.data, 1)


        return output
        # # max = out_arr[0]
        # # idx = 0
        # # maxidx = 0
        # # for i in out_arr:
        # #     if i> max: 
        # #         max = i
        # #         maxidx = idx
        # #     idx += 1

        # # return classes[maxidx]
    def NNTestSet(modelName,classes,loader):
        model = MyNeuralNetwork(len(classes))
        model.load_state_dict(torch.load(modelName))
        model.eval()
        correct = 0
        total = 0
        criterion = nn.CrossEntropyLoss()
        with torch.no_grad():
            for images, labels in loader['test_loader']:
                device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                val_loss += loss.item() * images.size(0)

        val_loss = val_loss / len(loader['test_loader'])
        val_acc = correct / total

        print(val_acc)



    def ResNetTrain(loader,save_name,epochs,classes):
        model = resnet50(weights='ResNet50_Weights.DEFAULT')
        print(model)
        num_classes = len(classes)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.SGD(model.parameters(), lr=0.01,momentum=0.9,weight_decay=1e-5)
        scheduler = lr_scheduler.LinearLR(optimizer, start_factor=1.0, end_factor=0.01, total_iters=epochs)
        history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
        best_val_acc = 0
        print('begin')
        for epoch in range(epochs): 
            # --- Training Phase ---
            model.train()
            running_loss = 0.0
            correct = 0
            total = 0
            
            for images, labels in loader['train_loader']:
                images, labels = images.to(device), labels.to(device)
                
                # Forward pass
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                # Backward và optimize
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                # Tính accuracy
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                running_loss += loss.item() * images.size(0)
            
            before_lr = optimizer.param_groups[0]["lr"]
            scheduler.step()
            after_lr = optimizer.param_groups[0]["lr"]
            print("Epoch %d: SGD lr %.4f -> %.4f" % (epoch, before_lr, after_lr))
            
            train_loss = running_loss / len(loader['train_loader'])
            train_acc = correct / total
            history['train_loss'].append(train_loss)
            history['train_acc'].append(train_acc)
            
            # --- Validation Phase ---
            model.eval()
            val_loss = 0.0
            correct = 0
            total = 0
            
            with torch.no_grad():
                for images, labels in loader['val_loader']:
                    images, labels = images.to(device), labels.to(device)
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                    
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()
                    val_loss += loss.item() * images.size(0)
            
            val_loss = val_loss / len(loader['val_loader'])
            val_acc = correct / total
            history['val_loss'].append(val_loss)
            history['val_acc'].append(val_acc)
            print(train_acc)
            print(val_acc)
            #Preventing Overfitting
            if(train_acc>0.85 and train_acc-val_acc>0.1):
                pass

            #Saving Best models
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save(model.state_dict(), f'{save_name}.pth')
            
            #Result
            print(f'Epoch [{epoch+1}/20], '
                f'Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, '
                f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}')

        print(f'Best Validation Accuracy: {best_val_acc:.4f}')

    def ResNetTest(modelName,img,classes):
        model = resnet50(weights='ResNet50_Weights.DEFAULT')
        num_classes = len(classes)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        model.load_state_dict(torch.load(modelName))
        image = Image.open(img)
        transform = transforms.Compose([
            transforms.Grayscale(3),
            transforms.Resize((224,224)),
            transforms.ToTensor(), 
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        tensor = transform(image)
        batch = tensor.unsqueeze(0)
        model.eval()
        with torch.no_grad():
            output = model(batch)
            prob = F.sigmoid(output)
            pred_class = torch.argmax(prob, dim=1)
            prob = torch.max(prob).tolist()


        return (classes[pred_class],prob)