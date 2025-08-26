#!/usr/bin/env python3
"""
脚本用于将vault目录中的def和pl文件替换到workspace目录中
在复制前会自动备份原文件
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime


def backup_file(file_path):
    """备份文件，添加时间戳后缀"""
    if not os.path.exists(file_path):
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    try:
        shutil.copy2(file_path, backup_path)
        print(f"已备份: {file_path} -> {backup_path}")
        return backup_path
    except Exception as e:
        print(f"备份失败 {file_path}: {e}")
        return None


def copy_def_files(workspace_dir, vault_dir):
    """复制def和pl文件从vault到workspace"""
    
    workspace_path = Path(workspace_dir)
    vault_path = Path(vault_dir)
    
    if not workspace_path.exists():
        print(f"错误: workspace目录不存在: {workspace_dir}")
        return False
    
    if not vault_path.exists():
        print(f"错误: vault目录不存在: {vault_dir}")
        return False
    
    print(f"Workspace目录: {workspace_dir}")
    print(f"Vault目录: {vault_dir}")
    print("-" * 50)
    
    # 遍历workspace目录下的case
    for case_dir in workspace_path.iterdir():
        if not case_dir.is_dir():
            continue
            
        case_name = case_dir.name
        print(f"\n处理case: {case_name}")
        
        # 构建vault中对应的路径
        vault_case_path = vault_path / f"{case_name}.density0.6" / case_name
        
        if not vault_case_path.exists():
            print(f"  跳过: vault中未找到case目录 {vault_case_path}")
            continue
        
        # 查找def和pl文件
        def_file = vault_case_path / f"{case_name}.def"
        pl_file = vault_case_path / f"{case_name}.pl"
        
        # 构建目标路径
        target_dir = case_dir / "pnr" / "build" / case_name / "bookshelf"
        target_def = target_dir / f"{case_name}.def"
        target_pl = target_dir / f"{case_name}.pl"
        
        # 检查目标目录是否存在
        if not target_dir.exists():
            print(f"  跳过: 目标目录不存在 {target_dir}")
            continue
        
        # 复制def文件
        if def_file.exists():
            print(f"  复制def文件: {def_file.name}")
            if target_def.exists():
                backup_file(target_def)
            try:
                shutil.copy2(def_file, target_def)
                print(f"    成功: {def_file} -> {target_def}")
            except Exception as e:
                print(f"    失败: {e}")
        else:
            print(f"  跳过: vault中未找到def文件 {def_file}")
        
        # 复制pl文件
        if pl_file.exists():
            print(f"  复制pl文件: {pl_file.name}")
            if target_pl.exists():
                backup_file(target_pl)
            try:
                shutil.copy2(pl_file, target_pl)
                print(f"    成功: {pl_file} -> {target_pl}")
            except Exception as e:
                print(f"    失败: {e}")
        else:
            print(f"  跳过: vault中未找到pl文件 {pl_file}")
    
    print("\n" + "=" * 50)
    print("文件替换完成！")


def main():
    parser = argparse.ArgumentParser(
        description="将vault目录中的def和pl文件替换到workspace目录中"
    )
    parser.add_argument(
        "workspace_dir", 
        help="workspace目录路径"
    )
    parser.add_argument(
        "vault_dir", 
        help="vault目录路径"
    )
    
    args = parser.parse_args()
    
    copy_def_files(args.workspace_dir, args.vault_dir)


if __name__ == "__main__":
    main()
