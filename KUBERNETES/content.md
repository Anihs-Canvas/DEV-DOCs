Kubernetes API

Workload Resources
this is the link to the official documentation: https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/


SECTION
Pod
this is the link to the official documentation: https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/pod-v1/



TABLE OF CONTENT
Pod
PodSpec
    Containers
    Volumes
    Scheduling
    Lifecycle
    Hostname and Name resolution
    Hosts namespaces
    Service account
    Security context
    Alpha level
    Deprecated
Container
    Image
    Entrypoint
    Ports
    Environment variables
    Volumes
    Resources
    Lifecycle
    Security Context
    Debugging
EphemeralContainer
    Image
    Entrypoint
    Environment variables
    Volumes
    Resources
    Lifecycle
    Debugging
    Security context
    Not allowed
LifecycleHandler
NodeAffinity
PodAffinity
PodAntiAffinity
Probe
PodStatus
PodList
Operations
    get read the specified Pod
    get read ephemeralcontainers of the specified Pod
    get read log of the specified Pod
    get read resize of the specified Pod
    get read status of the specified Pod
    list list or watch objects of kind Pod
    list list or watch objects of kind Pod
    create create a Pod
    update replace the specified Pod
    update replace ephemeralcontainers of the specified Pod
    update replace resize of the specified Pod
    update replace status of the specified Pod
    patch partially update the specified Pod
    patch partially update ephemeralcontainers of the specified Pod
    patch partially update resize of the specified Pod
    patch partially update status of the specified Pod
    delete delete a Pod
    deletecollection delete collection of Pod