import torch
import time

def test_gpu_speed():
    # 检查GPU是否可用
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    if device.type == 'cuda':
        print(f"GPU型号: {torch.cuda.get_device_name(0)}")
    
    # 创建大矩阵
    size = 50000
    a = torch.randn(size, size).to(device)
    b = torch.randn(size, size).to(device)
    
    # 测试矩阵乘法
    start = time.time()
    c = torch.mm(a, b)
    torch.cuda.synchronize()  # 等待GPU完成
    end = time.time()
    
    print(f"矩阵乘法 {size}x{size} 耗时: {end-start:.4f} 秒")
    
test_gpu_speed()