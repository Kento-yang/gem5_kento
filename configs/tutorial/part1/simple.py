#导入m5和SimObjects
import m5
from m5.objects import *
 
#创建要模拟的系统
system = System()
#设置系统时钟。1、建立时钟域，2、设置时钟频率，3、为时钟域指定电压域
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()
 
#设置系统模拟内存(计时模式)，设置内存范围
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]
 
#创建CPU（基于时间），
system.cpu = TimingSimpleCPU()
 
#创建系统范围内存总线
system.membus = SystemXBar()
 
#将CPU上的缓存端口连接到内存总线上。由于没有建立缓存cache，所以将icache和dcache直接连接到membus(本示例中没有缓存)
#         request port = response port
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports
 
#连接CPU的其他端口以确保系统可以正常工作，例如I/O控制器。
system.cpu.createInterruptController()
#将系统的一个特殊端口连接到menbus，这个端口只允许系统读写内存。
system.system_port = system.membus.cpu_side_ports
 
#x86的特定要求，将PIO和中断端口连接到内存总线.ARM指令集不需要此操作
if m5.defines.buildEnv['TARGET_ISA'] == "x86":
    system.cpu.interrupts[0].pio = system.membus.mem_side_ports
    system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports
 
#创建一个内存控制器，并将其连接到内存总线。这里使用的是DDR3控制器，负责内存的范围。
system.mem_ctrl = MemCtrl()
system.mem_ctrl.port = system.membus.mem_side_ports
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]

#模拟的System图:
#######################################################
#-----------------------CPU--------------------------
#       cpu.dcache_port     cpu.icache_port
#             ^                   ^
#             |                   |
#             |                   |
#             v                   v
#---------------------membus------------------------
#                       ^                   
#                       |                   
#                       |                   
#                       v  
#                  mem_ctrl.port
#--------------------mem_ctrl------------------------
########################################################

#---------------------设置CPU执行的进程--------------------#
#这里使用syscall仿真模式
# 1、设置可执行文件，2、创建进程，设置进程执行的可执行文件，
# 3、将进程设置为CPU的工作负载，4、在CPU上创建进程（或者说创建执行环境）
binary = 'tests/test-progs/hello/bin/x86/linux/hello'
 
#对于gem5 v21及更高版本，加入下面一行。
system.workload = SEWorkload.init_compatible(binary)
 
process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()
 
#---------实例化系统并执行-------------#
#创建根对象，并实例化模拟
root = Root(full_system = False,system = system)
m5.instantiate()
 
#开始模拟。这里的print不是语句而是作为一个函数被调用。
print("Beginning simulation")
exit_event = m5.simulate()
 
#模拟结束后对系统进行检测
print('Exiting @ tick {} because {}'
    .format(m5.curTick(),exit_event.getCause()))
 