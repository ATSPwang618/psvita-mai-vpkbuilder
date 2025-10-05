import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import subprocess
import threading
from pathlib import Path
import json

class VitaVPKBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("PS Vita VPK Builder")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # 默认路径
        self.default_paths = {
            "tools_dir": r"C:\Users\26241\Desktop\test\tools",
            "output_dir": r"C:\Users\26241\Desktop\test\output",
            "game_dir": r"C:\Users\26241\Desktop\test\Artemis-game\KZJJ00001"
        }
        
        self.setup_gui()
        self.load_settings()
    
    def setup_gui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="PS Vita VPK Builder", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 路径设置区域
        paths_frame = ttk.LabelFrame(main_frame, text="路径设置", padding="10")
        paths_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        paths_frame.columnconfigure(1, weight=1)
        
        # 游戏目录
        ttk.Label(paths_frame, text="游戏目录:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.game_dir_var = tk.StringVar(value=self.default_paths["game_dir"])
        game_dir_entry = ttk.Entry(paths_frame, textvariable=self.game_dir_var, width=50)
        game_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(paths_frame, text="浏览", 
                  command=lambda: self.browse_directory(self.game_dir_var)).grid(row=0, column=2, pady=2)
        
        # 工具目录
        ttk.Label(paths_frame, text="工具目录:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.tools_dir_var = tk.StringVar(value=self.default_paths["tools_dir"])
        tools_dir_entry = ttk.Entry(paths_frame, textvariable=self.tools_dir_var, width=50)
        tools_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(paths_frame, text="浏览", 
                  command=lambda: self.browse_directory(self.tools_dir_var)).grid(row=1, column=2, pady=2)
        
        # 输出目录
        ttk.Label(paths_frame, text="输出目录:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.output_dir_var = tk.StringVar(value=self.default_paths["output_dir"])
        output_dir_entry = ttk.Entry(paths_frame, textvariable=self.output_dir_var, width=50)
        output_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(paths_frame, text="浏览", 
                  command=lambda: self.browse_directory(self.output_dir_var)).grid(row=2, column=2, pady=2)
        
        # 游戏信息显示区域（只读）
        info_frame = ttk.LabelFrame(main_frame, text="游戏信息 (自动检测)", padding="10")
        info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        # Title ID (只读显示)
        ttk.Label(info_frame, text="Title ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.title_id_var = tk.StringVar()
        self.title_id_label = ttk.Label(info_frame, textvariable=self.title_id_var, 
                                       font=("Arial", 9, "bold"), foreground="blue")
        self.title_id_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # 游戏标题 (只读显示)
        ttk.Label(info_frame, text="游戏标题:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.game_title_var = tk.StringVar()
        self.game_title_label = ttk.Label(info_frame, textvariable=self.game_title_var,
                                         font=("Arial", 9, "bold"), foreground="blue")
        self.game_title_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(button_frame, text="检测游戏信息", 
                  command=self.detect_game_info).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="开始打包", 
                  command=self.start_packaging).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="保存设置", 
                  command=self.save_settings).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="清空日志", 
                  command=self.clear_log).grid(row=0, column=3, padx=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="打包日志", padding="10")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def browse_directory(self, var):
        """浏览并选择目录"""
        directory = filedialog.askdirectory(initialdir=var.get())
        if directory:
            var.set(directory)
    
    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def detect_game_info(self):
        """检测游戏信息"""
        game_dir = self.game_dir_var.get()
        if not os.path.exists(game_dir):
            messagebox.showerror("错误", "游戏目录不存在！")
            return
        
        # 从目录名提取Title ID
        title_id = os.path.basename(game_dir)
        self.title_id_var.set(title_id)
        
        # 尝试从param.sfo提取游戏标题（简单实现）
        param_sfo_path = os.path.join(game_dir, "sce_sys", "param.sfo")
        if os.path.exists(param_sfo_path):
            self.game_title_var.set(f"{title_id} Game")
            self.log_message(f"检测到游戏: Title ID = {title_id}")
        else:
            messagebox.showwarning("警告", "未找到 param.sfo 文件")
        
        # 检查必要文件
        required_files = [
            "eboot.bin",
            "sce_sys/param.sfo",
            "sce_sys/icon0.png"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = os.path.join(game_dir, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if missing_files:
            self.log_message("警告: 缺少以下必要文件:")
            for file_path in missing_files:
                self.log_message(f"  - {file_path}")
        else:
            self.log_message("✓ 所有必要文件检查完成")
    
    def check_tools(self):
        """检查工具是否存在"""
        tools_dir = self.tools_dir_var.get()
        required_tools = [
            "vita-pack-vpk.exe",
            "vita-mksfoex.exe"
        ]
        
        missing_tools = []
        for tool in required_tools:
            tool_path = os.path.join(tools_dir, tool)
            if not os.path.exists(tool_path):
                missing_tools.append(tool)
        
        if missing_tools:
            messagebox.showerror("错误", f"缺少以下工具:\n" + "\n".join(missing_tools))
            return False
        
        return True
    
    def start_packaging(self):
        """开始打包过程"""
        if not self.check_tools():
            return
        
        # 自动检测游戏信息
        if not self.title_id_var.get().strip():
            self.detect_game_info()
            if not self.title_id_var.get().strip():
                messagebox.showerror("错误", "无法检测游戏信息，请检查游戏目录")
                return
        
        # 在新线程中执行打包
        threading.Thread(target=self.package_vpk, daemon=True).start()
    
    def package_vpk(self):
        """执行VPK打包"""
        try:
            # 停止不确定进度条，改用确定进度
            self.progress_bar.config(mode='determinate')
            self.progress_var.set(0)
            
            self.log_message("=" * 60)
            self.log_message("🚀 开始 VPK 打包过程...")
            self.log_message("=" * 60)
            
            game_dir = self.game_dir_var.get()
            tools_dir = self.tools_dir_var.get()
            output_dir = self.output_dir_var.get()
            title_id = self.title_id_var.get().strip()
            
            # 步骤1: 创建输出目录 (5%)
            self.progress_var.set(5)
            self.log_message("📁 [步骤 1/6] 创建输出目录...")
            os.makedirs(output_dir, exist_ok=True)
            self.log_message(f"   ✓ 输出目录: {output_dir}")
            
            # 步骤2: 扫描游戏文件 (15%)
            self.progress_var.set(15)
            self.log_message("🔍 [步骤 2/6] 扫描游戏文件...")
            files_to_add = self.get_game_files(game_dir)
            self.log_message(f"   ✓ 找到 {len(files_to_add)} 个文件需要打包")
            
            # 显示部分文件列表
            if len(files_to_add) > 0:
                self.log_message("   📋 主要文件包括:")
                for i, (local_path, _) in enumerate(files_to_add[:8]):
                    self.log_message(f"      • {local_path}")
                if len(files_to_add) > 8:
                    self.log_message(f"      ... 以及其他 {len(files_to_add)-8} 个文件")
            
            # 步骤3: 构建打包命令 (25%)
            self.progress_var.set(25)
            self.log_message("⚙️ [步骤 3/6] 构建打包命令...")
            vpk_path = os.path.join(output_dir, f"{title_id}.vpk")
            vita_pack_tool = os.path.join(tools_dir, "vita-pack-vpk.exe")
            
            cmd = [
                vita_pack_tool,
                "-s", os.path.join(game_dir, "sce_sys", "param.sfo"),
                "-b", os.path.join(game_dir, "eboot.bin"),
                vpk_path
            ]
            
            # 添加所有游戏文件
            for local_path, vpk_path_in_archive in files_to_add:
                cmd.extend(["-a", f"{local_path}={vpk_path_in_archive}"])
            
            self.log_message(f"   ✓ 工具路径: {vita_pack_tool}")
            self.log_message(f"   ✓ 目标文件: {vpk_path}")
            
            # 步骤4: 开始打包 (35%)
            self.progress_var.set(35)
            self.log_message("📦 [步骤 4/6] 开始执行打包...")
            self.log_message("   正在调用 vita-pack-vpk 工具...")
            
            # 执行打包命令
            process = subprocess.Popen(
                cmd,
                cwd=game_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 合并输出
                text=True,
                encoding='utf-8',
                errors='ignore',
                bufsize=1,
                universal_newlines=True
            )
            
            # 步骤5: 监控打包过程 (35-85%)
            self.log_message("⏳ [步骤 5/6] 监控打包进度...")
            output_lines = []
            progress_step = 0
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    output_lines.append(line)
                    self.log_message(f"   > {line}")
                    
                    # 模拟进度更新
                    progress_step += 1
                    current_progress = min(35 + (progress_step * 2), 85)
                    self.progress_var.set(current_progress)
            
            # 等待进程完成
            process.wait()
            
            # 步骤6: 验证结果 (90-100%)
            self.progress_var.set(90)
            self.log_message("✅ [步骤 6/6] 验证打包结果...")
            
            if process.returncode == 0:
                self.progress_var.set(100)
                self.log_message("🎉 VPK 打包成功完成!")
                self.log_message("-" * 40)
                
                # 获取文件信息
                if os.path.exists(vpk_path):
                    file_size = os.path.getsize(vpk_path)
                    size_mb = file_size / (1024 * 1024)
                    self.log_message(f"📁 VPK 文件位置: {vpk_path}")
                    self.log_message(f"📊 文件大小: {size_mb:.2f} MB ({file_size:,} 字节)")
                    self.log_message(f"🎮 Title ID: {title_id}")
                    self.log_message(f"📦 包含文件: {len(files_to_add)} 个")
                    
                    self.log_message("=" * 60)
                    self.log_message("✨ 打包完成！可以将 VPK 文件传输到 PS Vita 安装")
                    self.log_message("=" * 60)
                    
                    messagebox.showinfo("打包成功", 
                        f"🎉 VPK 打包完成!\n\n"
                        f"📁 文件位置: {vpk_path}\n"
                        f"📊 文件大小: {size_mb:.2f} MB\n"
                        f"🎮 Title ID: {title_id}")
                else:
                    self.log_message("⚠️ 警告: VPK 文件未找到")
                    messagebox.showwarning("警告", "打包似乎成功，但找不到输出文件")
            else:
                self.progress_var.set(0)
                self.log_message(f"❌ 打包失败，错误代码: {process.returncode}")
                self.log_message("错误输出:")
                for line in output_lines:
                    if line.strip():
                        self.log_message(f"   {line}")
                messagebox.showerror("打包失败", 
                    f"VPK 打包失败\n错误代码: {process.returncode}\n请查看日志获取详细信息")
                
        except Exception as e:
            self.progress_var.set(0)
            self.log_message(f"💥 异常错误: {str(e)}")
            messagebox.showerror("异常错误", f"打包过程中发生异常:\n{str(e)}")
        finally:
            # 恢复进度条模式
            if self.progress_var.get() < 100:
                self.progress_bar.config(mode='indeterminate')
                self.progress_bar.stop()
    
    def get_game_files(self, game_dir):
        """获取游戏中需要打包的所有文件"""
        files_to_add = []
        
        # 定义需要包含的文件和目录
        include_patterns = [
            "sce_sys/icon0.png",
            "sce_sys/pic0.png", 
            "sce_sys/livearea/contents/background.png",
            "sce_sys/livearea/contents/startup.png",
            "sce_sys/livearea/contents/template.xml",
            "sce_module/*.suprx",
            "sce_sys/about/*.suprx",
            "sce_sys/manual/*.png",
            "sce_sys/package/*.bin",
            "font/*",
            "movie/**/*",
            "savedata-pc/*",
            "artemisengine.exe",
            "pfs_upk.exe", 
            "root.pfs",
            "system.ini"
        ]
        
        for pattern in include_patterns:
            if "*" in pattern:
                # 处理通配符
                if "**" in pattern:
                    # 递归搜索
                    base_path = pattern.split("**")[0].rstrip("/")
                    self.add_files_recursive(game_dir, base_path, files_to_add)
                else:
                    # 单层通配符
                    base_path = pattern.split("*")[0].rstrip("/")
                    if os.path.exists(os.path.join(game_dir, base_path)):
                        for item in os.listdir(os.path.join(game_dir, base_path)):
                            item_path = os.path.join(base_path, item)
                            full_path = os.path.join(game_dir, item_path)
                            if os.path.isfile(full_path):
                                files_to_add.append((item_path, item_path.replace("\\", "/")))
            else:
                # 精确文件路径
                full_path = os.path.join(game_dir, pattern)
                if os.path.exists(full_path):
                    files_to_add.append((pattern, pattern.replace("\\", "/")))
        
        return files_to_add
    
    def add_files_recursive(self, game_dir, base_path, files_to_add):
        """递归添加目录中的所有文件"""
        full_base_path = os.path.join(game_dir, base_path)
        if not os.path.exists(full_base_path):
            return
            
        for root, dirs, files in os.walk(full_base_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, game_dir)
                files_to_add.append((rel_path, rel_path.replace("\\", "/")))
    
    def save_settings(self):
        """保存设置到JSON文件"""
        settings = {
            "game_dir": self.game_dir_var.get(),
            "tools_dir": self.tools_dir_var.get(),
            "output_dir": self.output_dir_var.get(),
            "title_id": self.title_id_var.get(),
            "game_title": self.game_title_var.get()
        }
        
        try:
            with open("vpk_builder_settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.log_message("设置已保存")
            messagebox.showinfo("成功", "设置已保存到 vpk_builder_settings.json")
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")
    
    def load_settings(self):
        """从JSON文件加载设置"""
        try:
            if os.path.exists("vpk_builder_settings.json"):
                with open("vpk_builder_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                
                self.game_dir_var.set(settings.get("game_dir", self.default_paths["game_dir"]))
                self.tools_dir_var.set(settings.get("tools_dir", self.default_paths["tools_dir"]))
                self.output_dir_var.set(settings.get("output_dir", self.default_paths["output_dir"]))
                self.title_id_var.set(settings.get("title_id", ""))
                self.game_title_var.set(settings.get("game_title", ""))
                
                self.log_message("设置已加载")
        except Exception as e:
            self.log_message(f"加载设置失败: {str(e)}")

def main():
    root = tk.Tk()
    app = VitaVPKBuilder(root)
    root.mainloop()

if __name__ == "__main__":
    main()