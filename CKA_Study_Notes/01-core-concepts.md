# 01. Core Concepts

## Core Concepts

### Thanks Naveen 🙂

### Kubernetes Architecture

We start with a basic overview of the Kubernetes cluster architecture. We first look at the architecture at a high level and then we drill down into each of these components, we see what their roles and responsibilities are and how they are configured.

And finally, you go through a practice test where you look at an existing cluster and are asked to identify various details with respect to these components in the cluster.

We're going to use an analogy of ships to understand the architecture of Kubernetes. The purpose of Kubernetes is to host your applications in the form of containers in an automated fashion, so that you can easily deploy as many instances of your application as required and easily enable communication between different services within your application.

So there are many things involved that work together to make this possible.So let's take a 10000 feet look at the Kubernetes architecture. 

We have two kinds of ships. In this example cargo ships that do the actual work of carrying containers across to sea and control ships that are responsible for monitoring and managing the cargo ships.The Kubernetes cluster consists of a set of nodes which may be physical or virtual on-premise or on cloud that host applications in the form of containers. These relate to cargo ships.

In this analogy, the worker nodes in the cluster are ships that can load containers.But somebody needs to load the containers on the ships and not just load plan how to load identify the right ships store information about the ships monitor and track the location of containers on the ships manage the whole loading process etc.. This is done by the control ships that host different offices and departments, monitoring equipment, communication equipment, cranes for moving containers between ships etc. The control ships relate to the master node in the Kubernetes cluster the master node is responsible for managing the Kubernetes cluster storing information regarding the different nodes planning which containers cause where monitoring the nodes and containers on them etc. The Master node does all of these using a set of components together known as the **control plane components**.

⇒We will look at each of these components now.

Now there are many containers being loaded and unloaded from the ships on a daily basis.And so you need to maintain information about the different ships, what container is on which ship and what time it was loaded etc. All of these are stored in a highly available key value store known as **ETCD**, the ETCD is a database that stores information in a key-value format. We will look more into what ETCD cluster actually is what data is stored in it and how it stores the data in one of the upcoming lectures.

When ships arrive you load containers on them using cranes, the cranes identify the containers that need to be placed on ships. It identifies the right ship based on its size, its capacity, the number of containers already on the ship and any other conditions such as the destination of the ship, the type of containers it is allowed to carry etc. So those are **schedulers** in a Kubernetes cluster, as scheduler identifies the right node to place a container on based on the **container's resource requirements, the** worker nodes capacity or any other policies or constraints such as **taints and tolerations** or **node affinity rules** that are on them.

We will look at these in much more detail with examples and practice tests later in this course. We have a whole section on scheduling alone.

There are different offices in the dock that are assigned to special tasks or departments. For example the operations team takes care of ship handling traffic control etc. they deal with issues related to damages, the routes, the different ship state etc. The cargo team takes care of containers when containers  are damaged or destroyed, they make sure new containers are made available. 

You have these services offices that take care of the I.T. and communications between different ships.Similarly, in Kubernetes we have **controllers** available that take care of different areas. The **node-controller** takes care of nodes. They're responsible for onboarding new nodes to the cluster handling situations where nodes become unavailable or gets destroyed and the **replication controller** ensures that the desired number of containers are running at all times in your replication group.

So we have seen different components like the different offices, the different ships, the data store and the cranes.

**But how do these communicate with each other? How does one office reach the other office and who manages them all at a high level ?**

The **kube-apiserver** is the primary management component of kubernetes. The kube-api server is responsible for orchestrating all operations within the cluster. It exposes the Kubernetes API which is used by external users to perform management operations on the cluster as well as the various controllers to monitor the state of the cluster and make the necessary changes as required and by the worker nodes to communicate with the server. Now we are working with containers here. **Containers** are everywhere so we need everything to be container compatible. Our applications are in the form of containers. The different components that form the entire  management system on the master nodes could be hosted in the form of containers.

The **DNS service**, **networking solution** can all be deployed in the form of containers. So we need this software that can run containers and that's the **container runtime engine**. 

A popular one being **Docker**.So we need Docker or it's supported equivalent installed on all the nodes in the cluster including the master nodes if you wish to host the control plane components as containers. 

Now it doesn’t always have to be Docker. Kubernetes supports other runtime engines as well like **ContainerD** or Rkt. let's now turn our focus onto the cargo ships. Now every ship has a captain. The captain is responsible for managing all activities on these ships. The captain is responsible for liaising with the master ships starting with letting the master ship know that they are interested in joining the group receiving information about the containers to be loaded on the ship and loading the appropriate containers as required sending reports back to the master about the status of this ship and the status of the containers on the ship etc.

Now the captain of the ship is the **kubelet** in Kubernetes. A kubelet is an agent that runs on each node in a cluster. It listens for instructions from the kube-api server and deploys or destroys containers on the nodes as required.

The kube-api server periodically fetches status reports from the kubelet to monitor the state of nodes and containers on them. The kubelet was more of a captain on the ship that manages containers on the ship. But the applications running on the worker nodes need to be able to communicate with each other. 

For example you might have a web server running in one container on one of the nodes and a database server running on another container on another node. How would the web server reach the database server on the other node? Communication between worker nodes are enabled by another component that runs on the worker node known as the **Kube-proxy** service. The Kube-proxy service ensures that the necessary rules are in place on the worker nodes to allow the containers running on them to reach each other. So to summarize we have master and worker nodes. On the master. we have the **ETCD cluster** which stores information about the cluster, we have the **Kube scheduler** that is responsible for scheduling applications or containers on Nodes, We have different controllers that take care of different functions like the **node-control**, **replication-controller** etc.. We have the **Kube-api server** that is responsible for orchestrating all operations within the cluster. 

On the worker node.we have the **kubelet** that listens for instructions from the **Kube-apiserver** and manages containers and the **kube-proxy** that helps in enabling communication between services within the cluster.

So that's a high level overview of the various components.

We will drill down into each of these in the upcoming lectures.

### ETCD For Beginners

This is a quick introduction to ETCD for beginners. We start with a basic introduction to what a key value store is and how it is different from traditional databases, how to quickly get started with ETCD and how to use the client tool to operate ETCD. Later In this course, when we cover high availability, we will discuss about what it means to be a distributed system, how ETCD works in a cluster mode, what **RAFT** protocol is, and what are the best practices around the number of nodes  in the kubernetes cluster.

**So what is ETCD?** It is a distributed, reliable key value store that is simple, secure and fast.

So let's break it up.

![Diagram](images/image60.png)

**So what is a key value store,** traditionally, databases have been in a tabular format, you must have heard about sql or relational databases. They store data in the form of rows and columns. For example, here's a table that stores information regarding a few individuals.The row represents each person and the column represents the type of information being stored.

A key value store stores information in a key and a value format. You put a key and a value and it saves that in the database and then you get the key and it returns the value and you cannot have duplicate keys as such. It is not used as a replacement for a regular traveler database. Instead, it is used to store and retrieve small chunks of data, such as configuration data that requires fast read and writes

It's easy to install and get started with ETCD download the binary extract it and run, download the relevant binary for your operating system from the GitHub releases pages, extract it and run the executable. When you run ETC, it starts a service that listens on port 2379 by default. You can then attach any clients to the service to store and retrieve information. 

A default Client that comes with ETCD is the **ETCD control client.** The ETCD control client is a command line client for ETCD You can use it to store and retrieve key value pairs. To store a key value pair from the ETCD control set key one command followed by the value, value one. This creates an entry in the database with the information. To retrieve the stored data, run the ETCD control, get key one command.

![Diagram](images/image148.png)

To view more options from the outside control command without any argument. 

Well, that's a quick introduction to the ETCD. 

### ETCD in Kubernetes

In this  lesson we will talk about ETCD’s role in kubernetes. The ETCD datastore stores information regarding the cluster such as the **nodes, pods, configs, secrets, accounts, roles, bindings and others.**

Every information you see when you run the kubectl get command is from the ETCD server, every change you make to your cluster, such as adding additional nodes, deploying pods or ReplicaSets are updated in the ETCD server. Only once it is updated in the ETCD server, is the change considered to be complete. Depending on how you set up your cluster, ETCD is deployed differently. Throughout this section we discuss about two types of kubernetes deployment. One deployed from scratch and the other using the kubeadm tool.

The practice test environments are deployed using the kubeadm tool, and later in this course when we set up a cluster we set it up from scratch, so it's good to know the difference between the two methods, if you set up your cluster from scratch then you deploy ETCD by downloading the ETCD binaries yourself, installing the binaries and configuring ETCD as a service in your master node yourself. There are many options passed into the service. A number of them relate to certificates. We will learn more about these certificates, how to create them and how to configure them later In this course. We have a whole section on TLS certificates. The others are about configuring ETCD as a cluster. We will look at those options  when we set up high availability in kubernetes the only option to note for now is the **advertised client url.**

![Diagram](images/image42.png)

This is the address on which ETCD listens. It happens to be on the IP of the server and on port 2379, which is the default port on which etcd listens. This is the URL that should be configured on the kube-api server when it tries to reach the etcd server. If you setup your cluster using kubeadm then kubeadm deploys the ETCD server for you as a POD in the **kube-system namespace**. You can explore the etcd database using the etcdctl utility within this pod. To list all keys stored by kubernetes, run the **etcdctl get** command like this.

![Diagram](images/image230.png)

Kubernetes stores data in the specific directory structure, the root directory is a registry and under that you have the various kubernetes constructs such as **minions** or **nodes**, **pods**, **replicasets**, **deployments** etc. In a high availability environment you will have multiple master nodes in your cluster then you will have multiple ETCD instances spread across the master nodes. 

![Diagram](images/image87.png)

In that case, make sure to specify the ETCD instances know about each other by setting the right parameter in the ETCD service configuration. The initial-cluster option is where you must specify the different instances of the ETCD service. We talk about high availability in much more detail later in this course but I thought it's  worthwhile to point it out here.

### ETCD - Commands

ETCDCTL is the CLI tool used to interact with ETCD.

ETCDCTL can interact with ETCD Server using 2 API versions - **Version 2** and **Version 3.**  By default it is set to use Version 2. Each version has different sets of commands.

For example ETCDCTL version 2 supports the following commands:

```bash
etcdctl backup
etcdctl cluster-health
etcdctl mk
etcdctl mkdir
etcdctl set
```

Whereas the commands are different in version 3

```bash
etcdctl snapshot save
etcdctl endpoint health
etcdctl get
etcdctl put
```

To set the right version of API set the environment variable ETCDCTL_API command `export ETCDCTL_API=3`

When API version is not set, it is assumed to be set to version 2. And version 3 commands listed above don't work. When API version is set to version 3, version 2 commands listed above don't work.

Apart from that, you must also specify a path to certificate files so that ETCDCTL can authenticate to the ETCD API Server. The certificate files are available in the etcd-master at the following path. We discuss more about certificates in the security section of this course. So don't worry if this looks complex:

```text
--cacert /etc/kubernetes/pki/etcd/ca.crt    
--cert /etc/kubernetes/pki/etcd/server.crt    
--key /etc/kubernetes/pki/etcd/server.key
```

So for the commands I showed in the previous video to work you must specify the ETCDCTL API version and path to certificate files. Below is the final form:

```bash
kubectl exec etcd-master -n kube-system -- sh -c "ETCDCTL_API=3 etcdctl get / --prefix --keys-only --limit=10 --cacert /etc/kubernetes/pki/etcd/ca.crt --cert /etc/kubernetes/pki/etcd/server.crt  --key /etc/kubernetes/pki/etcd/server.key"
```

### kube-api Server

In this lecture we will talk about the kube-API server in kubernetes. Earlier we discussed that the kube-api server is the primary management component in kubernetes. When you run a kubectl command, the kubectl utility is infact reaching to the kube-apiserver. The kube-api server first authenticates the request and validates it. It then retrieves the data from the ETCD cluster and responds back with the requested information. 

You don’t really need to use the kubectl command line. Instead, you could also invoke the API directly by sending a **post** request like this 

![Diagram](images/image214.png)

Let's look at an  example of creating a pod when you do that as before the request is authenticated first and then validated. In this case, the API server creates a POD object without assigning it to a node, updates the information in the ETCD server and updates the user that the POD has been created.

![Diagram](images/image246.png)

- The scheduler continuously monitors the API server and realizes that there is a new pod with no node assigned, → the scheduler identifies the right node to place the new POD on and communicates that back to the kube-apiserver. → The API server then updates the information in the ETCD cluster. → The API server then passes that information to the kubelet in the appropriate worker node. → The kubelet then creates the POD on the node and instructs the container runtime engine to deploy the application image.

Once done, the kubelet updates the status back to the API server and the API server then updates the data back in the ETCD cluster. A similar pattern is followed every time a change is requested. The kube-apiserver is at the center of all the different tasks that needs to be performed to make a change in the cluster.

**To summarize, the kube-api server is responsible for Authenticating and validating requests, retrieving and updating data in ETCD data store,** in fact, kube-api server is the only component that interacts directly with the etcd datastore.

The other components such as the scheduler, kube-controller-manager & kubelet uses the API server to perform updates in the cluster in their respective areas. 

If you bootstrapped your cluster using kubeadm tool then you don't need to know this but if you are setting up the hard way, then kube-apiserver is available as a binary in the kubernetes release page. Download it and configure it to run as a service on your kubernetes master node.

![Diagram](images/image55.png)

The kube-api server is run with a lot of parameters as you can see here. Throughout this section we are going to take a peek at how to install and configure these individual components of the kubernetes architecture.

You don't have to understand all of the options right now but I think having a high level understanding on some of these now will make it easier later when we configure the whole cluster and all of its components from scratch. The kubernetes architecture consists of a lot of different components working with each other, talking to each other in many different ways so they all need to know where the other components are. **There are different modes of authentication, authorization, encryption and security.** And that’s why you have so many options when we go through the relevant section in the course we will pull up this file and look at the relevant options.

For now we will look at a few important ones. A lot of them are certificates that are used to secure the connectivity between different components. We look at these certificates in more detail when we go through the SSL/TLS certificates lecture later in this course. 

There is a whole section just for it. So we will get rid of them for now. But just remember all of the various components we are going to look at in this section will have certificates associated with them. The option ETCD-servers is where you specify the location of the ETCD servers. This is how the kube-api server connects to the etcd servers.

![Diagram](images/image94.png)

![Diagram](images/image313.png)

 So how do you view the kube-api server options in an existing cluster It depends on how you set up your cluster If you set it up **with kubeadm tool**, kubeadm deploys the kube-api server as a pod in the **kube-system namespace** on the master node.  you can see the options within the pod definition file located at  **/etc/kubernetes/manifests** folder. etc kubernetes manifests folder.

In a non kubeadm setup you can inspect the options by viewing kube-apiserver service located at `/etc/systemd/system/kube-apiserver.service.`You can also see the running process and the effective options by listing the process on the master node and searching for kube-apiserver.

![Diagram](images/image157.png)

ou can also see the running process and affective options by listing the process on master node and searching for kube-apiserver.

![Diagram](images/image25.png)

`$ ps -aux | grep kube-apiserver`

### KUBE-CONTROLLER Manager

**Kube Controller Manager**. As we discussed earlier, the kube controller manager manages various controllers in Kubernetes. A controller is like an office or department within the master ship that have their own set of responsibilities. Such as an office for the Ships would be responsible for monitoring and taking necessary actions about the ships, whenever a new ship arrives or when a ship leaves or gets destroyed, another office could be one that manages the containers on the ships. They take care of containers that are damaged or fall off ships.

So these offices are :1.  Continuously on the lookout for the status of the ships and 2.  Take necessary actions to remediate the situation. 

In the kubernetes terms a controller is a process that continuously monitors the state of various components within the system and works towards bringing the whole system to the desired functioning state.

![Diagram](images/image330.png)

For example the **Node-Controller** is responsible for monitoring the status of the nodes and taking necessary actions to keep the application running. It does that through the **kube-api** server. The node controller checks the status of the nodes every 5 seconds. That way the node controller can monitor the health of the nodes if it stops receiving heartbeat from a node, The node is marked as unreachable but it waits for 40 seconds before marking it unreachable, After a node is marked unreachable it gives it five minutes to come back up, if it doesn’t, it removes the PODs assigned to that node and provisions them on the healthy ones. If the PODs are part of a **replica-set.** 

![Diagram](images/image202.png)

The next controller is the **replication controller**. It is responsible for monitoring the status of ReplicaSets and ensuring that the desired number of PODs are available at all times within the set. If a pod dies it creates another one. 

![Diagram](images/image264.png)

Now those were just two examples of controllers. There are many more such controllers available within kubernetes. Whatever concepts we have seen so far in kubernetes such as deployments, Services, namespaces, persistent volumes and whatever intelligence is built into these constructs it is implemented through these various controllers.

As you can imagine this is kind of the brain behind a lot of things in kubernetes. **Now how do you see these controllers and where are they located in your cluster?**

They're all packaged into a single process known as **kubernetes controller manager**.

When you install the kubernetes controller manager the different controllers get installed as well.

So how do you install and view the **kubernetes controller manager?** Download the **kube-controller-manager** from the kubernetes release page. Extract it and run it as a service.

```text
$ wget https://storage.googleapis.com/kubernetes-release/release/v1.13.0/bin/linux/amd64/kube-controller-manager
$ cat /etc/systemd/system/kube-controller-manager.service
```

![Diagram](images/image288.png)

When you run it as you can see there are a list of options provided this is where you provide additional options to customize your controller. Remember some of the default settings for node controller we discussed earlier such as the node monitor period the grace period and the eviction timeout.  These go in here as options. There is an additional option called controllers that you can use to specify which controllers to enable. By default  all of them are enabled but you can choose to enable a select few. So in case any of your controllers don't seem to work or exist this would be a good starting point to look at.

**So how do you view the Kube-controller-manager server options?**

Again it depends on how you set up your cluster. If you set it up with kubeadm tool, kubeadm deploys the **kube-controller-manager** as a pod in the kube-system namespace on the master node. You can see the options within the pod definition file located at etc kubernetes manifests folder. 

```text
$ cat /etc/kubernetes/manifests/kube-controller-manager.yaml
```

![Diagram](images/image305.png)

![Diagram](images/image32.png)

In a non-kubeadm setup, you can inspect the options by viewing the kube-controller-manager service located at the services directory. 

You can also see the running process and the effective options by listing the process on the master node and searching for kube-controller-manager. 

```bash
$ ps -aux | grep kube-controller-manager
```

![Diagram](images/image340.png)

### Kube Scheduler

**Kube Scheduler.** Earlier we discussed that the kubernetes scheduler is responsible for scheduling pods on nodes.

![Diagram](images/image311.png)

Now don't let the graphic mislead you. Remember the scheduler is only responsible for deciding which pod goes on which node. It doesn’t actually place the pod on the nodes. That’s the job of the kubelet. The kubelet or the captain on the ship is who creates the pod on the ships. The scheduler only decides which pod goes where. 

Let's look at how the scheduler does that in a bit more detail.

**First of all, why do you need a scheduler?**When there are many ships and many containers, You want to make sure that the right container ends up on the right ship. For example there could be different sizes of ships and containers. You want to make sure the ship has sufficient capacity to accommodate those containers, different ships maybe going to different destinations. You want to make sure your containers are placed on the right ships so they end up in the right destination. 

In kubernetes, the scheduler decides which nodes the pods are placed on  depending on certain criteria. You may have PODs with different resource requirements, You can have nodes in the cluster dedicated to certain applications. So how does the scheduler assign these PODs? The scheduler looks at each POD and tries to find the best node for it.

![Diagram](images/image51.png)

For example, let’s take one of these PODs. The big blue one. It has a set of CPU and Memory requirements. The scheduler goes through two phases to identify the best node for the pod in the first phase. The scheduler tries to filter out the nodes that do not fit the profile for this pod. For example, the nodes that do not have sufficient CPU and memory resources requested by the pod. So the first two small nodes are filtered out. So we are now left with two nodes on which the POD can be placed.

Now how does the scheduler pick one from the two, the scheduler ranks the node to identify the best fit for the pod. It uses a priority function to assign a score to the nodes on a scale of 0 to 10. For example the scheduler calculates the amount of resources that would be free on the nodes after placing the pod on them.  In this case, the one on the right would have 6 CPUs free if the pod was placed on it which is 4 more than the other one so it gets a better rank. And so it wins. **So that's how a scheduler works at a high level.**And of course these can be customized and you can write your own scheduler as well.  There are many more topics to look at such as **resource requirements**, **limits**, **taints and tolerations**, **node selectors**, **affinity rules** etc. Which is why we have an entire section dedicated to scheduling coming up in this course where we will discuss each of these in much more detail. For now we will continue to focus on the scheduler as a process at a high level. **So how do you install the kube-scheduler?**

![Diagram](images/image131.png)

![Diagram](images/image49.png)

Download the kube-scheduler from the kubernetes release page. Extract it and run it as a service. when you run it as a service. You specify the scheduler configuration file. `$ wget` [https://storage.googleapis.com/kubernetes-release/release/v1.13.0/bin/linux/amd64/kube-scheduler](https://storage.googleapis.com/kubernetes-release/release/v1.13.0/bin/linux/amd64/kube-scheduler)**So how do you view the kube-scheduler server options?**Again, if you set it up with kubeadm tool, kubeadm deploys the kube-scheduler as a pod in the kube-system namespace on the master node. You can see the options within the pod definition file located at /etc/kubernetes/manifests folder.`$ cat /etc/kubernetes/manifests/kube-scheduler.yaml` 

You can also see the running process and the effective options by listing the process on the master node and searching for kube-scheduler. 

![Diagram](images/image294.png)

`$ ps -aux | grep kube-scheduler`

### Kubelet

**K****ubelet**. Earlier we discussed that the kubelet is like the captain on the ship. They lead all activities on a ship. They're the ones responsible for doing all the paperwork necessary to **become part of the cluster**, They're the sole point of contact from the master ship. They **load or unload containers** on the ship as instructed by the scheduler on the master. They also send back reports at regular intervals on the status of the ship and the containers on them.  The kubelet in the kubernetes worker node, registers the node with the kubernetes cluster. When it receives instructions to load a container or a POD on the node, it requests the container run time engine, which may be Docker, to pull the required image and run an instance. The kubelet then continues to monitor the state of the POD and the containers in it and reports to the kube-api server on a timely basis.

![Diagram](images/image325.png)

So how do you install the kubelet? If you use kubeadm tool to deploy your cluster, it does not automatically deploy the kubelet. Now that's the difference from the other components. You must always manually install the kubelet on your worker nodes. Download the installer, extract it and run it as a service.

![Diagram](images/image53.png)

`$ wget` [https://storage.googleapis.com/kubernetes-release/release/v1.13.0/bin/linux/amd64/kubelet](https://storage.googleapis.com/kubernetes-release/release/v1.13.0/bin/linux/amd64/kubelet)

![Diagram](images/image90.png)

You can view the running kubelet process and the effective options by listing the process on the worker node and searching for kubelet.  `$ ps -aux |grep kubelet`We will look more into kubelets, how to configure kubelets, generate certificates, and finally how to TLS bootstrap kubelets later in this course.

### Kube Proxy.

![Diagram](images/image15.png)

Kube Proxy. Within a kubernetes cluster, every pod can reach every other pod. This is accomplished by deploying a POD networking solution to the cluster. A POD network is an internal virtual network that spans across all the nodes in the cluster to which all the PODs connect to. Through this network we are able to communicate with each other. There are many solutions available for deploying such a network.

In this case I have a web application deployed on the first node and a database application deployed on the second. The web app can reach the database, simply by using the IP of the database POD. But there is no guarantee that the IP of the database POD will always remain the same. 

![Diagram](images/image224.png)

If you've gone through the lecture on services as discussed in the beginners course you must know that a better way for the web application to access the database is using a service. So we create a service to expose the database application across the cluster.  The web application can now access the database using the name of the service db. The service also gets an IP address assigned to it whenever a pod tries to reach the service using its IP or name it forwards the traffic to the back-end pod. In this case the database.**But what is this service and how does it get an IP?**  **Does the service join the same POD Network?**The service cannot join the pod network because the service is not an actual thing. It is not a container like pod so it doesn't have any interfaces or an actively listening process. It is a virtual component that only lives in the cabinet as memory. But then we also said that the service should be accessible across the cluster from any node. **So how is that achieved?** That’s where kube-proxy comes in. Kube-proxy is a process that runs on each node in the kubernetes cluster. **Its job is to look for new services and every time a new service is created it creates the appropriate rules on each node to forward traffic to those services** **to the backend pods**. One way it does this is using IPTABLES rules. In this case it creates an IP tables rule on each node in the cluster to forward traffic heading to the IP of the service which is **10.96.0.12** to the IP of the actual pod which is **10.32.0.15**. So thats how kube-proxy configure the service 

We discuss a lot more about networking and services kube-proxy and POD networking. Later in this course again we have a large section just for networking. 

We will now see how to install kube-proxy. Download the kube-proxy binary from the kubernetes release page. Extract it and run it as a service. 

```text
$ wget https://storage.googleapis.com/kubernetes-release/release/v1.13.0/bin/linux/amd64/kube-proxy
```

![Diagram](images/image235.png)

The kubeadm tool deploys kube-proxy as PODs on each node. In fact it is deployed as a daemon set, so a single POD is always deployed on each node in the cluster. Well if you don't know about daemon set yet don't worry we have a lecture on that coming up in this course. We have now covered a high-level overview of the various components in the kubernetes control plane. As mentioned we will look at some of these in much more detail at various sections in this course. `$ kubectl get pods -n kube-system`

![Diagram](images/image161.png)

### PODs

![Diagram](images/image151.png)

![Diagram](images/image76.png)

Before we head into understanding PODs , It is  assumed that the following have been set up already.At this point we assume that the application is already developed and built into Docker images and it is available on a Docker repository like Docker Hub, so kubernetes can pull it down. We also assume that the kubernetes cluster has already been set up and is working. This could be a single node set up or a multi node setup. Doesn't matter. All the services need to be in a running state. As we discussed before with kubernetes our ultimate aim is to deploy our application in the form of containers on a set of machines that are configured as worker nodes in a cluster. However, kubernetes does not deploy containers directly on the worker nodes. The containers are encapsulated into a kubernetes object known as pods. A pod is a single instance of an application. A pod is the smallest object that you can create in  kubernetes. Here we see the simplest of simplest cases where you have a single node kubernetes cluster with a  single instance of your application running in a single docker container encapsulated in a pod.

What if the number of users accessing your application increases and you need to scale your application, you need to add additional instances of your Web application to share the load. **Now, where would you spin up additional instances?**  **Do we bring up new container instances within the same pod?**

![Diagram](images/image383.png)

![Diagram](images/image43.png)

**No**, we create a new pod altogether with a new instance of the same application. As you can see, we now have two instances of our Web application running on two separate pods on the same kubernetes system or node. **What if the user base further increases and your current node has no sufficient capacity?**Well, then you can always deploy additional pods on a new node in the cluster, you will have a new node added to the cluster to expand the cluster’s physical capacity. So what I'm trying to illustrate in this slide is that pods usually have a one to one relationship with containers running your application to scale up. You create new pods to scaleup and to scale down you delete existing pods  *→* ***You do not add additional containers to an existing pod to scale your application****.*Also, if you're wondering how we implement all of this and how we achieve load balancing between the containers, etc., we will get into all of that in a later lecture.  We just said that PODs usually have a one to one relationship with the containers, **but are we restricted to having a single container in a single pod?** No, a single pod can have multiple containers, except for the fact that they're usually not multiple containers of the same kind.  

![Diagram](images/image215.png)

As we discussed in the previous slide. If our intention was to scale our application, then we would need to create additional pods. But sometimes you might have a scenario where you have a helper container that might be doing some kind of supporting task for our Web application, such as *processing a user entered data, processing a file uploaded by the user, etc.* and you want these helper containers to live alongside your application container. In that case, you can have both of these containers, part of the same pod, so that when a new application container is created, the helper is also created and when it dies, the helper also dies. Since they are part of the same pod, the two containers can also communicate with each other directly by referring to each other as localhost since they *share the same network space*, *plus they can easily share the same storage space as well*. If you still have doubts in this topic,I would understand If you did, because I did the first time I learned these concepts, we could take another shot at understanding PODs from a different angle. 

Let's for a moment keep kubernetes out of our discussion and talk about simple docker containers,Let's assume we were developing a process or a script to deploy our application on a Docker host. 

Then we would first simply deploy our application using a simple `docker run python-appt` command and the application runs fine and our users are able to access it. 

![Diagram](images/image114.png)

When the load increases, we deploy more instances of our application by running the `docker run` commands many more times. This works fine and we are all happy.Now sometime in the future Our application is further developed, undergoes architectural changes and grows and gets complex. 

We now have a new helper container that helps our web application by processing or fetching data from elsewhere. These helper containers maintain a one to one relationship with our application container and thus need to communicate with the application containers directly and access data from those containers. For this, we need to maintain a map of what app and helper containers are connected to each other, we would need to establish network connectivity between these containers ourselves using links and custom networks. We would need to create shareable volumes and shares among the containers. We would need to maintain a map of that as well.  And most importantly, we would need to monitor the state of the application container. And when it dies, manually  kill the helper container as well, as it's no longer required. When a new container is deployed, we would need to deploy the new helper container as well. **With PODs** kubernetes does all of this for us automatically, we just need to define what containers a POD consists of and the containers in a POD by default will have access to the same storage, the same network namespace and same fate as in. They will be created together and destroyed together.

Even if our application didn't happen to be so complex and we could live with a single container, kubernetes  still requires you to create pods. But this is good in the long run as your application is now equipped for architectural changes and scale in the future. However, also note that multiple containers are a rare use case and we are going to stick to single containers per pod in this course. 

Let us now look at how to deploy pods.

Earlier, we learned about the Kubectl run command, what the command really does is, it deploys a docker container by creating a pod.  It first creates a pod automatically and deploys an instance of the nginx docker image. But where does it get the application image from ? For that you need to specify the image name using the image parameter, the application image. In this case, the nginx image is downloaded from the Docker hub repository, Docker hub as we discussed, is a public repository where the latest images of various applications are stored.  You could configure kubernetes to pull the image from the public docker hub or a private repository within the organization. Now that we have a POD created, how do we see the list of PODs available? The `kubectl get pods` command helps us see the list of pods in our cluster, in this case, we see the pod is in a container creating state and soon changes to a running state when it is actually running. 

![Diagram](images/image177.png)

### PODs with YAML

We will talk about creating a pod using a Yaml based configuration file. In the previous lecture, we learned about Yaml files in general. Now we will learn how to develop YAML files specifically for kubernetes. Kubernetes, uses Yaml files as inputs for the creation of objects such as PODs, replicas, deployment's services, etc.. All of these follow a similar structure. A kubernetes definition file always contains four top level fields, the **apiVersion, kind, metadata and spec.**

These are the top level or root level properties. These are also required fields, so you must have them in your configuration file.  Let us look at each one of them.The first one is the **apiVersion**. This is the version of the kubernetes API we are using to create the object depending on what we are trying to create. We must use the right API version. For now. Since we are working on PODs, we will set the API version as we V1. Few other possible values for this field are **apps/v1** extensions/v1beta, etc..

![Diagram](images/image252.png)

We will see what these are later in this course. 

Next is the **kind**, the kind refers to, the type of object we are trying to create, which in this case happens to be a pod, so we will set it as Pod. Some other possible values here could be ReplicasSet or Deployment or Service, which is what you see in the kind field in the table on the top.The next is **metadata**. The metadata is data about the object, like its **name, labels,** et cetera. As you can see, unlike the first two where you have specified a string value, this is in the form of a dictionary. So everything under metadata is intended to the right a little bit, and so names and labels are children of metadata. The number of spaces before the two properties, name and labels, doesn't matter, but they should be the same, as they are siblings.

![Diagram](images/image286.png)

In this case, labels have more spaces on the left than name. And so it is now a child of the name property instead of a sibling, which is incorrect.

![Diagram](images/image197.png)

Also, the two properties must have more spaces than its parent, which is metadata, so that it's intended to the right a little bit in this case, all three of them have the same number of spaces before them and so they are all siblings, which is not correct. 

![Diagram](images/image115.png)

Under metadata, the name is a string value, so you can name your POD, myapp-pod. And the labels is a dictionary, so labels is a dictionary within the metadata dictionary.  And it can have any key and value pairs, as you wish. For now, I have added a label app with the value of myapp. Similarly, you could add other labels as you see fit, which will help you identify these objects at a later point in time. 

Say, for example, there are hundreds of pods running a frontend application and hundreds of PODs running a backend application or a database. It will be difficult for you to group these PODs once they are deployed. If you label them now as frontend, backend or database, you will be able to filter the PODs based on this label at a later point in time. 

It's important to note that under metadata you can only specify name or labels or anything else that kubernetes expects to be under metadata. You cannot add any other property as you wish under this. However, under labels you can have any kind of key or value pairs as you see fit. So it's important to  understand what each of these parameters expect. So far, we have only mentioned the type and name of the object we need to create, which happens to be a POD with the name myapp-pod. But we haven't really specified the container or image we need in the POD. The last section in the configuration file is the specification section, which is written as **spec** depending on the object we are going to create. This is where we would provide additional information to kubernetes pertaining to that object. This is going to be different for different objects. So it's important to understand or refer to the documentation section to get the right format for each. 

Since we are only creating a pod with a single container in it, it is easy. **Spec is a dictionary,** so add a property under it called containers, **containers is a list or an array**. The reason this property is a list is because the *pods can have multiple containers within them*, as we learned in the lecture earlier.  In this case, though, we will only add a single item in the list since we plan to have only a single container in the pod. The *dash right before the name indicates that this is the first item in the list*. The item in the list is a dictionary, so add a name and image property. The value for image is in nginx, which is the name of the Docker image in the Docker repository. Once the file is created from the command `kubectl create -f` followed by the file name, which is <POD definition file .yaml and kubernetes will create the POD. 

![Diagram](images/image206.png)

So to summarize, remember the four top level properties **apiVersion, kind of metadata and spec** then start by adding value to those depending on the object you are going to create. Once we create the pod, how do you see it use the `kubectl get pods` command to see a list of PODs available. Un this case, it's just want to see detailed information about the pod, run the `kubectl describe pod` command. This will tell you information about the pod when it was created, what labels are assigned to it, what docker containers are part of it, and the events associated with that pod.

### ReplicaSets and Replication Controller

We will discuss about Kuberntes controllers, controllers are the brains behind kubernetes, they are the processes that monitor Kuberntes objects and respond accordingly. In this lecture, we will discuss one controller in particular, and that is the **replication controller(end of life)**. **So what is a replica and why do we need a replication controller?** Let's go back to our first scenario where we had a single pod running our application. **What if for some reason our application crashes and the pod fails?**

Users will no longer be able to access our application, to prevent users from losing access to our application we would like to have more than one instance or pod running at the same time. That way, if one fails, we still have our application running on the other one, the replication controller helps us run multiple instances of a single pod in the kubernetes cluster, thus providing high availability. **So does that mean you can't use a replication controller if you plan to have a single pod?** No. Even if you have a single pod, the replication controller can help by automatically bringing up a new pod. When the existing one fails, thus replication controller ensures that the specified number of pods are running at all times, even if it's just one or hundred 

Another reason we need a **replication controller** is to create multiple PODs to share the load across them. For example, in this simple scenario, we have a single pod serving a set of users. When the number of users increases, we deploy additional pods to balance the load across the two pods. If the demand further increases and if we were to run out of resources on the first node, we could deploy additional PODs across the other nodes in the cluster. As you can see, the replication controller spans across multiple nodes in the cluster. It helps us balance the load across multiple pods on different nodes as well as scale our application when the demand increases.

![Diagram](images/image193.png)

It's important to note that there are two similar terms, **replication controller** and r**eplicasSet** both have the same purpose, but they are not the same. Replication controller is the older technology that is being replaced by replicaSet. ReplicaSet is the new recommended way to set up replication. However, whatever we discussed in the previous few slides remains applicable to both these technologies. There are minor differences in the way each works and we will look at that in a bit. As such, we will try to stick to ReplicaSets in all of our demos and implementations going forward. Let's now look at how we create a replication controller, as with the previous lecture, we start by creating a replication controller definition file. We will name **rc-defination.yaml**. As with any kubernetes definition file. We have four sections, the apiVersion, kind of metadata and spec. The apiversion is specific to what we are creating in this case  Replication controller is supported in kubernetes API, version V1. So we will set it as V1, the kind as we know is a **ReplicationController**.Under metadata, we will add a name and we will call it myapp-rc and we will also add a few labels, app and type and assign values to them. So far, it has been very similar to how we created a part in the previous section. The next is the most crucial part of the definition file, and that is the specification written as **spec**. For any kubernetes definition file the spec section defines what's inside the object we are creating. In this case, we know that the replication controller creates multiple instances of a POD, **but what POD?.** We create a template section under spec to provide a POD template to be used by the replication controller to create replicas. 

![Diagram](images/image378.png)

**Now, how do we define the template?**It's not that hard because we have already done that in the previous exercise. Remember, we created a pod definition file in the previous exercise. We could reuse the contents of the file to populate the **template** section. Move all the contents of the POD definition file into the template section of the replication controller, except for the first few lines which are apiVersion and kind. Remember, whatever we move must be under the template section, meaning they should be intended to the right and have more spaces before them than the template line itself. 

![Diagram](images/image85.png)

They should be children of the template section. Looking at our file now, we now have two metadata sections. One is for the replication controller and another for the pod. And we have two sections, one for each. We have nested to the finishing files together, the replication controller being the parent and the pod definition being the child. 

Now, there is something still missing, we haven't mentioned how many replicas we need in the replication controller for that, add another property to the spec called **replicas** and input the number of replicas you need under it. Remember that the template and replicas are direct children of spec sections. So there are siblings and must be on the same vertical line, 

![Diagram](images/image275.png)

```yaml
 apiVersion: v1
    kind: ReplicationController
    metadata:
      name: myapp-rc
      labels:
        app: myapp
        type: front-end
    spec:
     template:
        metadata:
          name: myapp-pod
          labels:
            app: myapp
            type: front-end
        spec:
         containers:
         - name: nginx-container
           image: nginx
     replicas: 3
```

which means having equal number of spaces before them. Once the file is ready, run the `kube create` command and input the file using the -f parameter. The replication controller is created, when the replication controller is created, it first creates the POD using the POD definition template as many as required, which is 3 in this case. To view the list of created replication controllers, run the `kubectl  get replication controller` command and you will see the replication controller listed. We can also see the desired number of replicas or PODs, the current number of replicas and how many of them are already in the output. If you would like to see the PODs that were created by the replication controller, run the `kubectl get pods` command and you will see three PODs running. **Note** that all of them are starting with the name of the replication controller, which is myapp-rc, indicating that they are all created automatically by the replication controller. 

![Diagram](images/image239.png)

What we just saw was the replication controller. Let us now look at **Replicaset**, it is very similar to a replication controller. As usual. First, we have an apiVersion kind, metadata and spec. The apiVersion, though, is a bit different. It is apps/V1, which is different from what we had before for the replication controller, which was just V1. If you get this wrong, you are likely to get an error that looks like this. 

![Diagram](images/image9.png)

It would say **no match for /,  kind=ReplicaSet** because the specified kubernetes API version has no support for ReplicaSet. The kind would be, like I said ReplicaSet , and we add name and labels in the metadata. 

![Diagram](images/image64.png)

The specification section looks very similar to the replication controller. It has a template section where we provide POD definition as before. So I'm going to copy the contents over from our definition file and we have a number of replicas, which is set to three. However, there is one major difference between replication controller and ReplicaSet. ReplicaSet requires a **selector definition**. The selector section helps the ReplicaSet identify 

what PODs fall under it.

```yaml
 apiVersion: apps/v1
    kind: ReplicaSet
    metadata:
      name: myapp-replicaset
      labels:
        app: myapp
        type: front-end
    spec:
     template:
        metadata:
          name: myapp-pod
          labels:
            app: myapp
            type: front-end
        spec:
         containers:
         - name: nginx-container
           image: nginx
     replicas: 3
     selector:
       matchLabels:
        type: front-end
```

**But why would you have to specify what PODs fall under it if we have provided the contents of the definition file itself in the template?** It's because ReplicaSet can also manage PODs that were not created as part of the ReplicaSet creation, say for example, there were PODs created before the creation of the ReplicaSet that matched **labels** specified in the **selector**. The ReplicaSet will also take those PODs into consideration when creating the replicas. I will elaborate this in the next slide, but before we get into that, I would like to mention that the **selector** is one of the major differences between replication controller and replicaSet, the selector is not a required field in case of a replication controller, but it is still available, when you skip it, as we did in the previous slide. It assumes it to be the same as the labels provided in the pod definition file. In the case of ReplicaSet, a user input is required for this property and it has to be written in the form of **matchlabels**, as shown here. The match labels selector simply matches the labels specified under it to the  labels on the POD. The **replicaSet** Selector also provides many other options for matching labels that were not available in the replication controller. And as always, to create a replicaSet, run the `kubectl create` command, providing the definition file as input and to see the created replicas run the `kubectl get` `replicaset` command, to get a list of pods, simply run the `kubectl get pods` command. 

![Diagram](images/image186.png)

So what is the deal with **labels and selectors,** why do we label our PODs and objects in kubernetes?Let us look at a simple scenario. Say we deployed three instances of our fron-end web application as three PODs. We would like to create a replication controller or replicaSet to ensure that we have three active PODs at any time and yes, that is one of the use cases of replicaSets. You can use it to monitor existing PODs if you have them already  created, as it is in this example, In case they were not created, the replicaSet will create them for you. The role of the ReplicaSet is to monitor the PODs and if any of them were to fail, deploy new ones. The ReplicaSet is in fact a *process that monitors the PODs.***Now, how does the replicaSet know what PODs to monitor?**There could be hundreds of other PODs in the cluster running different applications. *This is where labeling our pods during creation comes in handy*. We could now provide these labels as a filter for ReplicaSet under the **selector** section, we use to matchlabels filter and provide the same label that we used while creating the PODs this way. The replicaSet knows which PODs to monitor. The same concept of labels and collectors is used in many other places throughout kubernetes. 

![Diagram](images/image182.png)

Now, let me ask you a question along the same lines in the ReplicaSet specification section, we learned that there are three sections, **template replicas and the selector.** We need three replicas and we have updated our selector based on our discussion in the previous slide. Say, for instance, we have the same scenario as in the previous slide, where we have three existing PODs that were created already and we need to create a  replicaSet to monitor the PODs to ensure there are a minimum of three running at all times. When the replication controller is created, it is not going to deploy a new instance of pods as three of them with matching labels are already created 

In that case, do we really need to provide a template section in the replicaSet  specification ?, since we are not expecting the replicas to create a new POD on deployment? Yes, we do, because in case one of the PODs were to fail in the future, the ReplicaSet needs to create a new one to maintain the desired number of PODs and for the replicaSet to create a new POD, the template definition section is required. Let's now look at how we scale the concept, say we started with three replicas, in the future we decided to scale to six.  **How do we update our replicaSet to scale to six replicas?** Well, there are multiple ways to do it. The first is to update the number of replicas in the definition,  to 6. then run the `kubectl replace` command to specify the same file using the -f parameter, and that will update the ReplicaSet to have six replicas. 

```yaml
apiVersion: apps/v1
   kind: ReplicaSet
   metadata:
     name: myapp-replicaset
     labels:
       app: myapp
       type: front-end
   spec:
    template:
       metadata:
         name: myapp-pod
         labels:
           app: myapp
           type: front-end
       spec:
        containers:
        - name: nginx-container
          image: nginx
    replicas: 6
    selector:
      matchLabels:
```

       `type: front-end`The **second way** to do it is to run the `kubectl scale` command using the replicas parameter to provide the new number of replicas and specify the same file as input. 

![Diagram](images/image290.png)

![Diagram](images/image199.png)

You may either input the definition file or provide the ReplicaSet that name in the type name format. → However, remember that using the filename as input will not result in the number of replicas being updated automatically in the file. In other words, the number of replicas in the ReplicaSet definition file will still be three, even though you scaled your ReplicaSet to have six replicas using the `kubectl scale` command and the file as input. There are also options available for automatically scaling the ReplicaSet based on load, but that is an advanced topic and we will discuss it at a later time.  Let's review the command's real quick. The `kubectl create` command, as we know, is used to create a ReplicaSet or basically any object in kubernetes depending on the file we are providing as input, you must provide the input file using the `-f` parameter. Use the `kubectl get`  command to see list of ReplicaSet created, use the `kubeclt delete` `replicaset`  command followed by the name of the replica, said to delete the ReplicaSet. And then we have the `kubectl  replace` command to replace or update the ReplicaSet and also the `kubectl scale` command scale ReplicaSet simply from the command line without having to modify the file.

![Diagram](images/image101.png)

### Deployments

In this lecture we will discuss about Kubernetes Deployments. For a minute, let us forget about PODs and `ReplicaSet` and other kubernetes concepts and talk about how you might want to deploy your application in a production environment. Say for example you have a web server that needs to be deployed in a production environment. Firstly you need not one but many such instances of the web server running for obvious reasons. Secondly whenever newer versions of application builds become available on the docker registry you would like to upgrade your Docker instances seamlessly. However when you upgrade your instances you do not want to upgrade all of them at once as we just did. This may impact users accessing our applications, so you might want to upgrade them one after the other. And that kind of upgrade is known as rolling updates.

Suppose one of the upgrades you performed resulted in an unexpected error and you're asked to undo the recent change, you would like to be able to roll back the changes that were recently carried out. Finally, say for example you would like to make multiple changes to your environment such as upgrading the underlying WebServer versions, as well as scaling your environment and also modifying the resource allocations etc.You do not want to apply each change immediately after the command is run, instead you would like to apply a pause to your environment, make the changes and then resume so that all changes are rolled-out together. All of these capabilities are available with the kubernetes Deployments. 

So far in this course we discussed about PODs, which deploy single instances of our application such as the web application in this case. Each container is encapsulated in PODs. Multiple such PODs are deployed using Replication Controllers or Replica Sets. And then comes **Deployment** which is a kubernetes object that comes higher in the hierarchy. *The deployment provides us with the capability to upgrade the underlying instances seamlessly using rolling updates, undo changes, and pause and resume changes as required.* **So how do we create a deployment?** As with the previous components, We first create a deployment definition file. The contents of the deployment definition file are exactly similar to the ReplicaSet definition file, except for the kind, which is now going to be **Deployment**. If  we walk through the contents of the file it has an apiVersion which is `apps/v1`, metadata which has `name and labels` and a spec that has `template, replicas` and `selector.`The template has a pod definition inside it. Once the file is ready run the `kubectl create` command and specify the deployment definition file. Then run the `kubectl get deployments` command to see  the newly created deployment. *The deployment automatically creates a replica set.* So if you run the `kubectl get replcaset` command you will be able to see a new replica set in the name of the deployment. the replicasets ultimately create pods, so if you run the `kubectl get pods` command you will be able to see the pods with the name of the deployment and the replicaset. So far there hasn't been much of a difference between replica set and deployments except for the fact that deployments created a new kubernetes object called **deployments**. 

We will see how to take advantage of the deployment using the use cases we discussed in the previous slide in the upcoming lectures and one more note before we end this lecture. To see all the created objects at once run the `kubectl get all` command and in this case we can see that the deployment was created and then we have the replica set followed by three pods that were created as part of the deployment.

### Services

**Kubernetes Services** enable communication between various components within and outside of the application. Kubernetes services help us connect applications together with other applications or users.

 For example our application has groups of pods running various sections such as a group for serving front-end load to users and another group for running back-end processes and a third group connecting to an external data source. It is **services** that enables connectivity between these groups of pods. Services enable the front-end application to be made available to end users, it helps communication between back-end and front-end pods and helps in establishing connectivity to an external data source. Thus services enable loose coupling between micro services in our application.

![Diagram](images/image356.png)

#### NodePort

![Diagram](images/image67.png)

![Diagram](images/image326.png)

![Diagram](images/image368.png)

Let's take a look at one use case of services. So far we talked about how pods communicate with each other through internal networking. Let's look at some other aspects of networking. In this lecture let's start with external communication.  So we deployed our pod having a web application running on it. How do we as an external user access the web page? First of all let us look at the existing setup. The Kubernetes Node has an IP address and that is 192.168.1.2. My laptop is on the same network as well so it has an IP address 192.168.1.10. The internal POD network is in the range 10.244.0.0 and the POD has an IP 10.244.0.2. Clearly, I cannot ping or access the POD at address 10.244.0.2 as it's in a separate network. So what are the options to see the webpage? First, if we were to SSH into the kubernetes node at 192.168.1.2, from the node, we would be able to access the POD’s webpage by doing a curl or if the node has a GUI, we could fire up a browser and see the webpage in a browser following the address http://10.244.0.2. But this is from inside the kubernetes Node and that’s not what I really want. I want to be able to access the web server from my own laptop without having to SSH into the node and simply by accessing the IP of the kubernetes node. So we need something in the middle to help us map requests to the node from our laptop through the node to the POD running the web container. This is where the kubernetes service comes into play. The kubernetes service is an object just like PODs, Replicaset or Deployments that we worked with before. One of its use cases is to listen to a port on the Node and forward requests on that port to a port on the POD running the web application. This type of service is known as a **NodePort service** because the service listens to a port on the Node and forwards requests to PODs. There are other kinds of services available which we will now discuss. The first one is what we discussed already. **NodePort** where the service makes an internal POD accessible on a Port on the Node. The second is **ClusterIP**.  **ClusterIP**: And in this case the service creates a virtual IP inside the cluster to enable communication between different services such as a set of front-end servers to a set of back-end servers.  

![Diagram](images/image228.png)

The third type is a **LoadBalancer**, where it provisions a load balancer for our service in supported cloud providers. A good example of that would be to distribute load across the different web servers in your front-end tier.  We will now look at each of these in a bit more detail along with some demos. In this lecture we will discuss about the **NodePort** Kubernetes Service.Getting back to NodePort, Few slides back. We discussed about external access to the application. We said that a Service can help us by mapping a port on the Node to a port on the POD. Let’s take a closer look at the service. If you look at it there are three ports involved. 

- The port on the POD where the actual web server is running is 80 and it is referred to as the **targetPort** because that is where the service forwards the requests to.

- The second port is **the port on the service itself**; it is simply referred to as the **port**.

*Remember these terms are from the viewpoint of the service. The service is in fact like a virtual server inside the node Inside the cluster It has its own IP address and that IP address is called the* ***clusterIP*** *of the service.*

- And finally we have the port on the node itself which we use to access the web server externally and that is known as the node port.

![Diagram](images/image371.png)

![Diagram](images/image145.png)

As you can see it is 30008. That is because NodePorts can only be in a valid range which by default is from **30000 to 32767**. Let's now look at how to create the service. Just like how we created a Deployment, ReplicaSet or Pod, in the past we will use a definition file to create a service the high level structure of the file remains the same as before we have the **apiVersion,kind,metadata and spec** sections the apiVersion is going to be V1. The kind is of course Service, the metadata will have a name and that will be the name of the service. It can have labels but we don't need that for now. Next we have spec and as always this is the most crucial part of the file and that is where we will be defining the actual services and this is the part of a definition file that differs between different objects. In the spec section of a service. We have **type** and **ports** the type refers to the type of service we are creating. as discussed before it could be **clusterIP** **nodeport** or **load balancer.** In this case since we are creating a `NodePort` we will set it as `NodePort`. The next part of a spec is **Ports**. This is where we input information regarding what we discussed. The first type of port is the `targetPort` which we will set to 80 the next one is simply `port` which is a port on the service object and we will set that to 80 as well. The third is `nodePort`  which we will set to 30008 or any number in the valid range. 

```yaml
apiVersion: v1
kind: Service
metadata:
 name: myapp-service
spec:
 type: NodePort
 ports:
 - targetPort: 80
   port: 80
   nodePort: 30008
 selector:
   app: myapp
   type: front-end
```

Remember that out of these the only mandatory field is port if we don't provide a target port. It is assumed to be the same as port and if you don’t provide a nodePort a free port in the valid range between 30000 and 32767 is automatically allocated. Also note that ports is an array. So no the dash under the port section that indicates the first element in the array. You can have multiple such port mappings within a single service. So we have all the information in but something is really missing. There is nothing here in the definition file that connects the service to the pod. We have simply specified the target port but we didn't mention the target port on which pod there could be 100s of other PODs with web services running on port 80. So how do we do that as we did with the replica sets previously and a technique that you will see very often in kubernetes, we will use labels and selectors to link these together. We know that the POD was created with a label, we need to bring that label into the service definition file so we have a new property in the spec section and that is called selector. Just like in a replica set and deployment definition files under the selector provide a list of labels to identify the pod for this. Refer to the pod definition file used to create the pod pull the labels from the pod definition file and place it under the selector section. This links the service to the pod.  

Once done create the service using the `kubectl create` command and input the service-definition file and there you have the service created. To see the created service, run the `kubectl get services` command that lists the service, the cluster IP and the map port. The type is node port as we created and the port on the node is set to 30008 because that's the port that we specified in the definition file. We can now use this port to access the web service using curl or a web browser.

So curl to 192.168.1.2 which is the IP of the node and then use the port 30008 to access the web server.

**So far we talked about a service mapped to a single pod but that's not the case all the time. What do you do when you have multiple PODs?** 

In a production environment you have multiple instances of your web application running for high availability and load balancing purposes, in this case we have multiple similar pods running our web application they all have the same labels with a key **app** and set to a value of **myapp** the same label is used as a selector during the creation of the service. So when the service is created it looks for a matching pod with the label and finds three of them. The service then automatically selects all the three pods as endpoints to forward the external requests coming from the user. You don't have to do any additional configuration to make this happen. And if you're wondering what algorithm it uses to balance the load across the three different pods it uses a **random algorithm** does the service acts as a built in load balancer to distribute load across different pods 

And finally let us look at what happens when the pods are distributed across multiple nodes. In this case we have the web application on pods on separate nodes in the cluster, when we create a service without us having to do any additional configuration kubernetes automatically creates a service that spans across all the nodes in the cluster and maps the target port to the same node port on all the nodes in the cluster this way you can access your application using the IP of any node in the cluster and using the same port number which in this case is 30008 as you can see using the IP of any of these nodes. 

And I'm trying to curl to the same port and the same port is made available on all the nodes part of the cluster.

To summarize in any case whether it be a single pod on a single node multiple pods on a single node or multiple pods on multiple nodes the service is created exactly the same without you having to do any additional steps during the service creation when pods are removed or added. The service is automatically updated making it highly flexible and adaptive once created. You won't typically have to make any additional configuration changes

#### Services ClusterIP

![Diagram](images/image26.png)

![Diagram](images/image405.png)

We will discuss about the Kubernetes **Service - ClusterIP.**A full stack web application typically has different kinds of pods hosting different parts of an application. You may have a number of pods running a front-end web server, another set of pods running a back-end server, a set of PODs running a key-value store like Redis, another set of PODs running a persistent database like MySQL. The web front-end server needs to communicate to the back-end servers, and the back-end servers need to connect to a database as well as the redis services etc.. **So what is the right way to establish connectivity between these services or tiers of my application?** The pods all have an IP address assigned to them as we can see on the screen but these IPs as we know are not static. These pods can go down any time and new pods are created all the time. And so you cannot rely on these IP addresses for internal communication between the application. Also what if the first front-end POD at 10.244.0.3 needs to connect to a backend service? Which of the three would it go to and who makes that decision. A kubernetes service can help us group these PODs together and provide a single interface to access the PODs in a group. For example a service created for the backend PODs will help group all the backend PODs together and provide a single interface for other PODs to access this service. The requests are forwarded to one of the PODs under the service randomly. Similarly create additional services for Redis and allow the backend PODs to access the redis systems through the service. This enables us to easily and effectively deploy a microservices based application on a kubernetes cluster. Each layer can now scale or move as required without impacting communication between the various services. Each service gets an IP name assigned to it inside the cluster and that is the name that should be used by other pods to access the service. This type of service is known as **clusterIP.** To create such a service as always use a definition file in the service definition file, first used to default template which has apiVersion, kind, metadata and spec`apiVersion: v1`

```yaml
kind: Service
metadata:
 name: back-end
spec:
 types: ClusterIP
 ports:
 - targetPort: 80
   port: 80
 selector:
   app: myapp
   type: back-end
$ kubectl create -f service-definition.yaml
```

![Diagram](images/image265.png)

![Diagram](images/image27.png)

The apiVersion is V1 kind of Service and we will give a name to our service. We will call it backend under specification we have **type** and **ports** the type is clusterIP in fact clusterIP is the default type. So even if you didn't specify it it will automatically assume the type to be cluster IP under ports we have a **target port** and **port** the targetport is the port where the backend is exposed which in this case is 80 and the port is where the service is exposed which is 80 as well. To link the service to a set of pods we use `selector` we will refer to the **pod definition file** and copy the labels from it and remove it under selector and that should be it. We can now create the service using the `kubectl create` command and then check its status using the `kubectl get services` command. The service can be accessed by other PODs using the ClusterIP or the service name.

#### Services – Loadbalancer

![Diagram](images/image373.png)

![Diagram](images/image200.png)

![Diagram](images/image171.png)

So we have seen the nodePort service that helps us make an external facing application available on a port, on the worker nodes.So let's turn our focus to the front end applications, which are the voting-app and the result-app. Now, we know that these pods are hosted on the worker nodes in the cluster. So let's say we have a four node cluster and to make the applications accessible to external users, we create these services of type nodePort. Now the services with type nodeport help in receiving traffic on the ports on the notes and routing the traffic to the respective pods.**But what URL would you give your end users to access the applications?** You could access any of these two applications using IP of any of the nodes and the high port the services exposed on, so that would be four IP and port combinations, for the voting app and four IP and port combination for the result app,So note that. Even if your PODs are only hosted on two of the nodes, and they will still be accessible on IPs of all the nodes in the cluster.

Say the PODs for the voting app are only deployed on the nodes with IP 70 and 71, They would still be accessible on the ports of all the nodes in the cluster. So that's how a service is configured. So you would share these URLs to your users to access the application.  But that's not what the end users want. They need a single URL like **example-voting.com** or the **example-resultapp.com** to access the application. 

**So how do you achieve that now?** One way to achieve this is to create a new VM for a load balancer purpose and install and configure a suitable load balancer on it like HAproxy or nginx, etc. and then configure the load balancer to route traffic to the underlying nodes,  Now, setting all of that external load balancing and then maintaining and managing, that can be a tedious task. However, if we were on a supported cloud platform like Google Cloud or AWS or Azure, I could leverage the negative load balancer of that cloud platform. Kubernetes has support for integrating with the native load balancers of certain cloud providers and configuring that for us. So all you need to do is set the service type for the front end services to load balancer instead of nodePort.  

![Diagram](images/image136.png)

Now remember that this only works with separate cloud platforms, so GCP AWS and Azure are definitely supported. So if you set the type of service to loadBalancer. In an unsupportive environment like virtual box or any other environment, then it would have the same effect as setting it to Northport, where the services are exposed on a high end ports on the nodes there it just won't do any kind of external load balancer configuration. 

### Namespaces

We will discuss about namespaces in kubernetes, let us begin with an analogy. There are two boys named Mark to differentiate them from each other. We call them by their last names Smith and Williams. They come from different houses of course the Smiths and the Williams. There are other members in the house. The individuals within the house address each other simply by their first names.  For example the father addresses Mark simply as Mark. However if the father wishes to address the mark in the other house he would use the full name, someone outside of these houses would also use the full name to refer to the boys or anyone within these houses. Each of these houses have their own set of rules that defines who does what, each of these houses have their own set of resources that they can consume.

Now let's get back to kubernetes. These houses correspond to **namespaces** in kubernetes. So far in this course we've created objects such as pods, deployments and services in our cluster. Whatever we have been doing we have been doing within a namespace. We were inside a house all this while, this namespace is known as the **default namespace** and it is created automatically by kubernetes. When the cluster is first set up kubernetes creates a set of pods and services for its internal purpose such as those required by the networking solution, the DNS service etc. to isolate these from the user and to prevent you from accidentally deleting or modifying these services, kubernetes creates them under another namespace created at cluster startup named **kube-system** a third namespace created by kubernetes automatically is called **kube-public**. This is where resources that should be made available to all users are created. 

![Diagram](images/image327.png)

If your environment is small or your learning and playing around with a small cluster you shouldn't really have to worry about namespaces. You could continue to work in the default namespace. However as and when you grow and use a kubernetes cluster for enterprise or production purposes you may want to consider the use of namespaces, you can create your own namespaces as well. For example, if you wanted to use the same cluster for both **dev** and **production** environments but at the same time isolate the resources between them you can create a different namespace for each of them. That way while working in the **dev** environment you don't accidentally modify resources in **production**. 

![Diagram](images/image292.png)

![Diagram](images/image207.png)

![Diagram](images/image183.png)

![Diagram](images/image185.png)

![Diagram](images/image204.png)

![Diagram](images/image135.png)

Each of these namespaces can have its own set of policies that define who can do what. You can also assign a **quota of resources** to each of these namespaces that each namespace is guaranteed a certain amount of resources and does not use more than its allowed limit. Going back to the default namespace that we have been working on just like how the members within the House refer to each other by their first names. The resources within a namespace can refer to each other simply by their names in this case the **webapp** POD can reach the db-service simply using the hostname db-service If required the webapp Pod can reach a service in another namespace as well. For this you must append the name of the namespace to the name of the service. For example, for the web pod in the default namespace to connect to the database in the dev environment or namespace use the  <`servicename>.<namespace>.<svc>.cluster.<local` format that would be   `db-service.dev.svc.cluster.local` you're able to do this because when the service is created a DNS entry is added automatically in this format. Looking closely at the DNS name of the service. `mysql.connect(“db-service.dev.svc.cluster.local”)`The last part `cluster.local` is the default domain name of the kubernetes cluster; `svc` is the subdomain for service followed by the namespace and then the name of the service itself. Let us now look at some of the operational aspects of namespace. Let's start with the `kubectl` commands. For example, this command `kubectl get pods` is used to list all the pods but it only lists the pods in the default namespace to list pods in another namespace use the namespace option in the command along with the name of the namespace. In this case `kube-system`, 

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
  labels:
     app: myapp
     type: front-end
spec:
  containers:
  - name: nginx-container
    image: nginx
```

![Diagram](images/image28.png)

`$ kubectl create -f pod-definition.yaml``$ kubectl create -f pod-definition.yaml` `--namespace``=dev`here I have a pod definition file when you create a pod using this file. the pod is created in the default  namespace to create a pod in another namespace use the `--namespace` option, if you want to make sure that this POD gets created in the dev environment all the time even if you don't specify the namespace in the command line you can move the namespace definition into the pod definition file like this under the metadata section. 

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
  namespace: dev
  labels:
     app: myapp
     type: front-end
spec:
  containers:
  - name: nginx-container
    image: nginx
```

This is a good way to ensure your resources are always created in the same namespace. **So how do you create a new namespace like any other object?** Use an namespace definition file the apiVersion is v1 kind is Namespace and under metadata specify the name, in this case `dev` run the `kubectl create` command to create the namespace. 

![Diagram](images/image296.png)

Another way to create a namespace is by simply running the command `kubectl create namespace` followed by the name of the namespace now say we're working in three namespaces. As we discussed before, by default we are in the default namespace which is why we can see the resources inside the default namespace using the `kubectl get pods` command and to view those in the dev namespace we have to use the namespace option `-n` but what if we want to switch to the dev namespace permanently so that we don't have to specify the namespace option anymore well, in that case, use the `kubectl config` command to set the namespace in the current context **dev** you can then simply run the `kubectl get pods` command without the namespace option to list pods in the dev environment but you will need to specify the option for other environments such as **default** or **prod** similarly you can switch to the prod namespace the same way. 

Finally to view pods in all namespace use the `--all-namespace` option in the command. This will list all the pods in all of the namespace. Taking a closer look at the command. This command first identifies the current context and then sets the namespace to the desired one for that current context.

Well contexts are used to manage multiple clusters in multiple environments from the same management system. It is a totally separate topic to discuss and requires its own lecture so we will discuss context in another lecture to limit resources in a namespace.Create a resource quota to create one. Start with a definition file for resource quota specify the namespace for which you want to create the quota and then under spec provide your limits such as 10 pods 10 CPU units 10 GB byte of memory

### Imperative vs Declarative

So far, we have seen different ways of creating and managing objects in kubernetes. We created objects directly by running commands, as well as using object configuration files. Now, in the infrastructure as code world, there are different approaches in managing the infrastructure, and they are classified into imperative and declarative approaches.

Let's understand this with an analogy, let's say you want to visit a friend's house located at Street B. In the past, you would hire a taxi and give Step-By-Step instructions to the driver on how to reach the destination.

Mike, take right to street B, then take left to go to Street C and then take another left and then right to go to Street D and stop at the house.Specifying what to do and how to do  more importantly is the imperative approach.

![Diagram](images/image418.png)

On the other hand, today, when you book A Cab, say through Uber, you just specify the final destination, like “drive to Tom's house” and this is the declarative approach. In this case, we are not giving step by step instructions. Instead, we're just specifying the final destination. We're declaring the final destination and the system figures out the right path to reach the destination, specifying what to do, not how to do, is the declarative approach. **So what's that got to do with what we are learning?** **In the infrastructure as code world**, an example of an imperative approach of provisioning infrastructure would be a set of instructions written step by step, such as provisioning a VM named a web-server, installing the nginx software on it, editing configuration file to use port 8080 and setting the path to web files, downloading source code of repositories from GIT and finally, starting the nginx server.

So here we're saying what is required and also how to get things done. ^In the declarative approach we declare our requirements, for instance.

![Diagram](images/image413.png)

All we say is that we need a VM by the name web-server with the nginx software on it with a port set to 8080 and the path to the web files defined and where the source code of the application is  stored, and everything that's needed to be done to get this infrastructure in place is done by the system or the software.You don't have to provide Step-By-Step instructions. Orchestration tools like Ansible, Puppet or Chef or TerraForm fall into this category.  

*In the imperative approach,* ***what happens if the first time only half of the steps were executed?*** ***What happens if you provide the same set of instructions again to complete the remaining steps?*** *To handle such situations there will be many additional steps involved, such as checks to see if something already exists and taking an action based on the results of that check.* For instance, while provisioning a VM, what would happen if we went by the name web-server already exists. The same goes with creating a database or importing data, should it fail or should it continue since the VM is already there? What if we decide to upgrade the version of software to, say, nginx1.18 in the future?It should be as simple as updating the version of nginx in the configuration file, and the system should take care of the rest. Ideally, the system should be intelligent enough to know what has already been done and apply the necessary changes only. **That's the declarative way of doing things.** 

In the kubernetes world, the imperative way of managing infrastructure is using commands like the `kubectl run` command to create a pod, a `kubectl create deployment`, command to create a deployment. The `kubectl expose` command to create a service to expose the deployment, and the `kubectl edit` command may maybe used to edit an existing object, for scaling a deployment or replicaset `kubectl scale` command and update the image on a deployment we use the `kubectl set image` command. 

![Diagram](images/image10.png)

We have also used object configuration files to manage objects such as creating an object, using the `kubectl  create -f` command with the -f option to specify the object configuration file, and editing an object using the `kubectl replace` command and deleting an object using the `kubectl delete` command.

![Diagram](images/image66.png)

All of these are **imperative approaches** to managing objects in kubernetes. We are saying exactly how to bring the infrastructure to our needs by creating, updating or deleting objects. 

![Diagram](images/image195.png)

**The declarative approach** would be to create a set of files that defines the expected state of the applications and services on a kubernetes cluster, and with a single `kubectl apply` command kubernetes should be able to read the configuration files and decide by itself what needs to be done to bring the infrastructure to the expected state. So in the declarative approach, you will run the `kubectl apply` command for **creating, updating or deleting** an object.  The apply command will look at the existing configuration and figure out what changes need to be made to the system. So let's look at this in a bit more detail, now within the imperative approach there are two ways. The first is using imperative commands such as the `run create or expose` commands to create new objects and the `edit scale and set` commands to update existing objects. Now, these commands help in quickly creating or modifying objects, as we don't have to deal with YAML files and these are helpful during the certification exams. However, there are limited in functionality and will require forming long and complex commands for advanced use cases, such as creating a multi container POD or deployment.

![Diagram](images/image346.png)

Secondly, these commands are run once and forgotten. They are only available in a session history of the user who ran these commands. So it's hard for another person to figure out how these objects were created. So it is hard to keep track of and so it's difficult to work with these commands in large or complex environments. 

And that's where managing objects with the object configuration files can help. Creating object definition files or configuration files are manifest files, as it's also called, can help us write down exactly what we need the object to look like in a Yaml format and use that to create commands, to create the object.

We now have the YAML file with us always, and it can be saved in a code repository like Git. We can put together a change review and approval process around these files so that a change made is reviewed and approved before it is applied to a production environment. In the future if it changes to be made. For instance, editing the image name to another version there are different ways to go about it. One way is to use the `kubectl edit``,` command and specify the object name. So when this command is run, it opens a Yaml definition file similar to the one you used to create the object. But with some additional fields, such as the status fields that you see here, which are used to store the status of the pod, this is not the file you used to create the object. This is a similar POD definition file within the kubernetes  memory. You can make changes to this file and save and quit, and those changes will be applied to the live object. However, note that there is a difference between the live object and the definition file that you have locally. The change you made using the edit command is not really recorded anywhere. After the change is applied You're only left with your local definition file, which in fact has the old image name in it. In the future, say you are or a teammate decide to make a change to this object, unaware that a change was made using the `kubectl edit` command when the new change is applied, the previous change to the image is lost so you can use the kubectl edit command If you are making a change and you're sure that you're not going to rely on the object configuration file in the future, but a better approach to that is to first edit the local version of the object configuration file with the required changes and that is by updating the image name here and then running the `kubectl replace` command to update the object. This way, going forward, the changes made are recorded and can be tracked as part of the change review process. So at times you may want to completely delete and recreate objects, in such cases, you may run the same command, but with the force option like this. `--force`

![Diagram](images/image376.png)

Now, this is still the imperative approach because you're still instructed, kubernetes, how to create or update these objects.first, you run `kubectl create` command to create the object, and then you run the `replace` command to replace the object or `delete` command to delete the object.**And what if you run the create command** If the object already exists ? then it would fail with an error that says the POD already exists when  you update an object. You should always make sure that the object exists first before running the replace command. If an object does not exist, the replace command fails with an error message. So the imperative approach is very taxing for you as an administrator, as you must always be aware of the current configurations and perform checks to make sure that things are in place before making a change. 

![Diagram](images/image163.png)

The **declarative approach** is where you use the same object configuration files that we have been working on, but instead of the create or replace commands, we use the kubectl `apply` command  to manage objects, the kubectl `apply` command is intelligent enough to create an object if it doesn't already exist. If there are multiple object configuration files, as you would usually, then you must specify a **directory** as the path instead of a single file. That way, all the objects are created at once.  Now, when changes are to be made, we simply update the object configuration file and run the `kubectl apply` command again. And this time it knows that the object exists, and so it only updates the object with the new changes.So it never really throws an error that says “the object already exists or the object cannot be applied”. It will always figure out and the right approach to updating the object. So going forward, any changes made on the application, whether they're updating images or fields of existing configuration files or adding new configuration files altogether for new objects. All they do is simply update our local directory with the changes and then the kubectl apply command takes care of the rest. 

![Diagram](images/image269.png)

So we will discuss more about how the kubectl apply command works exactly in the backend in the next lecture. 

For now, let me give you some tips as part of the exam. So from an exam perspective, you could use the imperative approach to save time as much as possible. For example, if the question is to just create a pod or a deployment with a given image, then one of these imperative commands can help you achieve that quickly. So it's important to practice the imperative commands. If you need to edit a property of an existing object, then using the **kubectl edit** command may be the quickest way. If you have a complex requirement for, say, for example, that requires multiple containers, environment variables, commands, init containers, etc., then using an object configuration file to create the object would be preferred this way if you see that you made a mistake. You can easily update the file and apply it again and using the `kubectl apply` command that case would be a better option. So for more details on the different approaches to managing a kubernetes cluster, get yourself familiarized with the kubernetes  documentation pages. Create a pod called `httpd` using the image `httpd:alpine` in the default namespace. Next, create a service of type `ClusterIP` by the same name `(httpd)`. The target port for the service should be `80`.

```bash
kubectl run httpd --image=httpd:alpine --port=80 --expose
```

### Certification Tips - Imperative Commands with Kubectl

While you would be working mostly the declarative way - using definition files, imperative commands can help in getting one time tasks done quickly, as well as generate a definition template easily. This would help save a considerable amount of time during your exams.Before we begin, familiarize with the two options that can come in handy while working with the below commands: `--dry-run`: By default as soon as the command is run, the resource will be created. If you simply want to test your command , use the `--dry-run=client` option. This will not create the resource, instead, tell you whether the resource can be created and if your command is right.

- `-o yaml`: This will output the resource definition in YAML format on screen.Use the above two in combination to generate a resource definition file quickly, that you can then modify and create resources as required, instead of creating the files from scratch.

#### POD

**Create an NGINX Pod**`kubectl run nginx --image=nginx`

**Generate POD Manifest YAML file (-o yaml). Don't create it(--dry-run)**

```bash
kubectl run nginx --image=nginx --dry-run=client -o yaml
```

#### Deployment

**Create a deployment**`kubectl create deployment --image=nginx nginx`

**Generate Deployment YAML file (-o yaml). Don't create it(--dry-run)**`kubectl create deployment --image=nginx nginx --dry-run=client -o yaml` 

**Generate Deployment with 4 Replicas** `kubectl create deployment nginx --image=nginx --replicas=4`

**You can also scale a deployment using the kubectl scale command.**`kubectl scale deployment nginx --replicas=4`

**Another way to do this is to save the YAML definition to a file and modify**`kubectl create deployment nginx --image=nginx --dry-run=client -o yaml > nginx-deployment.yaml`

You can then update the YAML file with the replicas or any other field before creating the deployment.

#### Service

**Create a Service named redis-service of type ClusterIP to expose pod redis on port 6379** `kubectl expose pod redis --port=6379 --name redis-service --dry-run=client -o yaml`(This will automatically use the pod's labels as selectors)

Or`kubectl create service clusterip redis --tcp=6379:6379 --dry-run=client -o yaml` 

(This will not use the pods labels as selectors, instead it will assume selectors as **app=redis.** [You cannot pass in selectors as an option.](https://github.com/kubernetes/kubernetes/issues/46191) So it does not work very well if your pod has a different label set. So generate the file and modify the selectors before creating the service)

**Create a Service named nginx of type NodePort to expose pod nginx's port 80 on port 30080 on the nodes:**

```bash
kubectl expose pod nginx --type=NodePort --port=80 --name=nginx-service --dry-run=client -o yaml
```

(This will automatically use the pod's labels as selectors, [but you cannot specify the node port](https://github.com/kubernetes/kubernetes/issues/25478). You have to generate a definition file and then add the node port in manually before creating the service with the pod.)

Or

```bash
kubectl create service nodeport nginx --tcp=80:80 --node-port=30080 --dry-run=client -o yaml(This will not use the pods labels as selectors)
```

Both the above commands have their own challenges. While one of it cannot accept a selector the other cannot accept a node port. I would recommend going with the kubectl expose command. If you need to specify a node port, generate a definition file using the same command and manually input the nodeport before creating the service.[https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands)

[https://kubernetes.io/docs/reference/kubectl/conventions/](https://kubernetes.io/docs/reference/kubectl/conventions/) 

### KUBECTL APPLY

![Diagram](images/image31.png)

 The `kubectl apply` command takes into consideration the local configuration file, a live object definition on kubernetes and the last applied configuration before making a decision on what changes are to be made. So when you run the `kubectl apply` command, if the object does not already exist, the object is created, when the object is created an object configuration similar to what we created locally is created within kubernetes, but with additional fields to store status of the object. 

This is the live configuration of the object on the kubernetes cluster.This is how kubernetes internally stores information about an object no matter what approach you use to create the object.But when you use the kubectl  apply command to create an object, it does something a bit more, the YAML version of the local object configuration file we wrote is converted to a Jason format, and it is then stored as the last applied configuration, going forward for any updates to the object. All the three are compared to identify what changes are to be made on the live object.

![Diagram](images/image201.png)

 For example, say when the next image is updated to 1.19 in our local file and we run the apply command.This value is compared with the value in the live configuration and if there is a difference, the live configuration is updated with the new value. After any change the last applied Jason format is always updated to the latest so that it's always up to date.  

![Diagram](images/image37.png)

**So why do we then really need the last applied configuration, right?** So if a field was deleted, say, for example, the typed label was deleted, and now when we run the `kubectl apply` `command`, we see that the last applied configuration had a label, but it's not present in the local configuration, This means that the field needs to be removed from the live configuration. So if a field was present in the live configuration and not present in the local or the last applied configuration, then it will be left as is. But if a field is missing from the local field and it is present in the last applied configuration, so that means that in the previous step or whenever we ran the `kubectl apply` `command`, that particular field was there and it is now being removed. So the last applied configuration helps us figure out what field fields have been removed from the local file Right, so that field is then removed from the actual live configuration. What we just discussed is available for your reference in detail in the kubernetes document pages, so follow this link to view that. 

![Diagram](images/image318.png)

OK, so we saw the three sets of files and we know that the local file is what's stored on our local system. The live object configuration is in the kubernetes memory. But where is this Jason file that has the last applied configuration stored? Well, it's stored on the live object configuration on the kubernetes cluster itself as an annotation named **last applied configuration.**  So remember that this is only done when you use the apply command, `kubectl create or replace` commands do not store the last applied configuration like this. So you must bear in mind not to mix the imperative and declarative approaches while managing the kubernetes objects. So once you use the `kubectl apply`  command going forward, whenever a change is made, the `kubectl apply`  command compares all three sections. The local definition file, the live object configuration and the last applied configuration stored within the life object configuration file for deciding what changes are to be made to the live configuration, similar to what we saw in the previous slide.

---

### CustomResourceDefinitions (CRDs) & The Operator Pattern

Kubernetes is built to be extended. While built-in resources (Pods, Deployments, Services) cover standard workloads, modern platforms use **CustomResourceDefinitions (CRDs)** and **Operators** to manage stateful infrastructure natively.

#### 1. CustomResourceDefinition (`apiextensions.k8s.io/v1`)
A CRD registers new resource endpoints in the Kubernetes API backed by etcd storage.

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databases.company.org
spec:
  group: company.org
  names:
    kind: Database
    plural: databases
    singular: database
    shortNames: ["db"]
  scope: Namespaced
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            required: ["engine", "storage"]
            properties:
              engine:
                type: string
                enum: ["postgres", "mysql"]
              storage:
                type: string
    subresources:
      status: {}
```

#### 2. The Operator Pattern
A CRD provides the declarative schema, but has no operational intelligence. An **Operator** pairs a CRD with a **Custom Controller**:
- **Informer / Watch:** Watches custom resource events (Add/Update/Delete) over HTTP streaming.
- **Reconcile Loop:** Continuously compares observed state against `.spec` and creates or scales underlying StatefulSets, PVCs, and Secrets.
- **Autonomous Recovery:** Automates failover, point-in-time restores, and database schema migrations without human intervention.
