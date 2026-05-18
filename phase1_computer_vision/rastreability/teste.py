import cv2

# Verificar a versão do OpenCV
print(f"OpenCV version: {cv2.__version__}")

# Listar todos os atributos do módulo cv2
all_attributes = dir(cv2)

# Filtrar e listar os rastreadores disponíveis
trackers = [attr for attr in all_attributes if 'Tracker' in attr]
print("Rastreadores disponíveis em cv2:")
for tracker in trackers:
    print(tracker)
    
# Verificar se o módulo cv2.legacy está disponível
if hasattr(cv2, 'legacy'):
    legacy_attrs = dir(cv2.legacy)
    legacy_trackers = [attr for attr in legacy_attrs if 'Tracker' in attr]
    print("\nRastreadores disponíveis em cv2.legacy:")
    for tracker in legacy_trackers:
        print(tracker)
        
else:
    print("\nO modulo cv2.legacy não está disponível.")