"""Fix duplicate nodes entries in 6.3"""

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

old_dup = '''│   ├── 📄 cp-01, cp-02, cp-03
│   ├── 📄 wk-01, wk-02, wk-03, wk-04, wk-05
│   ├── 📄 cp-01, cp-02, cp-03              # → k8s.io.api.core.v1.Node
│   ├── 📄 wk-01, wk-02, wk-03, wk-04, wk-05  #   Contains: status.conditions (Ready,
│   └── 📄 fe-01, fe-02                      #     MemoryPressure, DiskPressure,
│                                            #     PIDPressure, NetworkUnavailable),
│                                            #     status.capacity (cpu, memory, pods,
│                                            #     ephemeral-storage), status.addresses
│                                            #     (InternalIP, Hostname), spec.taints,
│                                            #     spec.unschedulable, status.nodeInfo
│                                            #     (kubeletVersion, osImage,
│                                            #     containerRuntimeVersion, kernelVersion)'''

new_fixed = '''│   ├── 📄 cp-01, cp-02, cp-03            # → k8s.io.api.core.v1.Node
│   ├── 📄 wk-01, wk-02, wk-03, wk-04, wk-05#   Contains: status.conditions (Ready,
│   └── 📄 fe-01, fe-02                    #     MemoryPressure, DiskPressure,
│                                          #     PIDPressure, NetworkUnavailable),
│                                          #     status.capacity (cpu, memory, pods,
│                                          #     ephemeral-storage), status.addresses
│                                          #     (InternalIP, Hostname), spec.taints,
│                                          #     spec.unschedulable, status.nodeInfo
│                                          #     (kubeletVersion, osImage,
│                                          #     containerRuntimeVersion, kernelVersion)'''

if old_dup in html:
    html = html.replace(old_dup, new_fixed)
    print("Fixed duplicate nodes entries")
else:
    print("Pattern not found — searching...")
    idx = html.find('│   ├── 📄 cp-01, cp-02, cp-03\n│   ├── 📄 wk-01, wk-02, wk-03, wk-04, wk-05')
    if idx > 0:
        print(f"Found at index {idx}")
        print(repr(html[idx:idx+300]))
    else:
        print("Not found at all")

with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Final: {html.count(chr(10))} lines')
