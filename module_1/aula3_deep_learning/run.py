import torch
import torch.nn as nn # melhorar a rede
import torch.optim as optim # melhorar o modelo


# Modelo usa para aprender
X = torch.tensor([[5.0], [10.0], [10.0], [5.0], [10.0],
                  [5.0], [10.0], [10.0], [5.0], [10.0],
                  [5.0], [10.0], [10.0], [5.0], [10.0],
                  [5.0], [10.0], [10.0], [5.0], [10.0]], dtype=torch.float32)

# Resultados esperados
Y = torch.tensor([[30.5], [63.0], [67.0], [29.0], [62.0],
                  [30.5], [63.0], [67.0], [29.0], [62.0],
                  [30.5], [63.0], [67.0], [29.0], [62.0],
                  [30.5], [63.0], [67.0], [29.0], [62.0]], dtype=torch.float32)

# Estrutura com camadas que tem funções de ativação para aprender padrões

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # Atualizando para aceitar apenas 1 valor de entrada, pois agora temos apenas a distância
        self.fc1 = nn.Linear(1,5) # De 2 para 1 na entrada
        self.fc2 = nn.Linear(5,1)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        
        return x
    
model = Net()

criterion = nn.MSELoss()
optmizer = optim.SGD(model.parameters(), lr=0.01)

# Treinar a nossa rede através do loop

for epoch in range(1000):
    # Faz previsões e calcula quanto está errado (perda)
    optmizer.zero_grad()
    outputs = model(X)
    loss = criterion(outputs, Y)
    loss.backward()
    optmizer.step()
    
    if epoch % 100 == 99:
        print(f'Epoch {epoch+1}, Loss: {loss.item()}')
    