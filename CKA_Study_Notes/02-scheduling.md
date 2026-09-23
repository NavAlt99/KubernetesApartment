# 02. Scheduling

## SCHEDULER

### Manual Scheduling

**So if there is no scheduler to monitor and schedule nodes what happens?**

- The pods continue to be in a pending state.

**So what can you do about it ?** **-** You can manually assign pods to nodes yourself. Well without a scheduler,the easiest way to schedule a pod is to simply set the “nodeName” field to the name of the node in your pod specification file while creating the POD.  The pod then gets assigned to the specified node. You can only specify the node name at creation time. 

```yaml
apiVersion: v1
kind: Pod
metadata:
 name: nginx
 labels:
  name: nginx
spec:
 containers:
 - name: nginx
   image: nginx
   ports:
   - containerPort: 8080
 nodeName: node02
```

![Diagram](images/image395.png)

**What if the pod is already created and you want to assign the pod to a node?** 

- Kubernetes won’t allow you to modify the nodeName property of a pod.

![Diagram](images/image93.png)

**So another way to assign a node to an existing pod is to create a binding object** and send a post request to the pod’s binding API, thus mimicking what the actual scheduler does. In the binding object you specify a target node with the name of the node. Then send a post request to the pods binding API with the data set to the binding object in a JSON format.So you must convert the YAML file into its equivalent JSON format.

```yaml
#pod-bind-defination.yamlapiVersion: v1
kind: Binding
metadata:
  name: nginx
target:
  apiVersion: v1
  kind: Node
  name: node02
#pod-definition.yaml
apiVersion: v1
kind: Pod
metadata:
 name: nginx
 labels:
  name: nginx
spec:
 containers:
 - name: nginx
   image: nginx
   ports:
   - containerPort: 8080
curl --header "Content-Type:application/json" -- request POST --data {"apiVersion":"v1","kind":"Binding","metadata":{"name":"nginx"},"target":{"apiVersion":"v1","kind":"Node","name":"node02"}}
```

### Labels and Selectors

**What do we know about labels and selectors already ?**Labels and selectors are a standard method to group things together. Say you have a set of different **species**, a user wants to be able to filter them based on different criteria such as based on their **class** or **kind**, if they are **domestic** or **wild**, or see by their color and not just group. You want to be able to filter them based on a criteria such as all green animals or with multiple criteria such as everything green, that is also a bird.

![Diagram](images/image70.png)

![Diagram](images/image174.png)

![Diagram](images/image227.png)

![Diagram](images/image277.png)

Whatever that classification, maybe you need the ability to group things together and filter them based on your needs and the best way to do that is with **labels**. **Labels** or properties attached to each item.

![Diagram](images/image48.png)

So you add properties to each item for their class kind and color **selectors** help you filter these items.**For example when you say class equals mammal we get a list of mammals and when you say color equals green we get the green mammals** 

We see labels and selectors used everywhere such as the keywords you tag to YouTube videos or blogs that help users filter and find the right content. We see labels added to items in an online store that help you add different kinds of filters to view your products.

![Diagram](images/image71.png)

![Diagram](images/image301.png)

**So how are labels and selectors used in Kubernetes?**We have created a lot of different types of Objects in Kubernetes. Pods, Services, ReplicaSets and Deployments etc. For Kubernetes, all of these are different objects. Over time you may end up having hundreds or thousands of these objects in your cluster. Then you will need a way to **filter and view** different objects by different categories such as to group objects **by their type** 

or view objects **by application** 

![Diagram](images/image111.png)

or **by their functionality**

![Diagram](images/image409.png)

Whatever it may be. You can group and select objects using **labels and selectors** for each object attach labels as per your needs, like app, function etc. Then while selecting specify a condition to filter specific objects.

![Diagram](images/image374.png)

![Diagram](images/image159.png)

 **So how exactly do you specify labels in kubernetes?** In a pod-definition file, under metadata, create a section called labels. Under that add the labels in a key value format like this. You can add as many labels as you like. Once the pod is created, to select the pod with the labels use the kubectl get pods command along with the selector option, and specify the condition like `app=App1.`

```yaml
#pod-definition.yamlapiVersion: v1
 kind: Pod
 metadata:
  name: simple-webapp
  labels:
    app: App1
    function: Front-end
 spec:
  containers:
  - name: simple-webapp
    image: simple-webapp
    ports:
    - containerPort: 8080
$ kubectl get pods --selector app=App1
```

Kubernetes objects use labels and selectors internally to connect different objects together. For example, to create a replicaset consisting of 3 different pods, we first label the pod definition and use a selector in a replicaset to group the pods . In the replica-set definition file. You will see **labels** defined in two places.The labels defined under the template section are the labels configured on the pods. The labels you see at the top are the labels of the replicas set itself.

We're not really concerned about the labels of the replica set for now, because we are trying to get the replica set to discover the pods. The labels on the replica set will be used if you were to configure some other object to discover the replica set. In order to connect the replica set to the pod we configure the selector field under the  replica set specification to match the labels defined on the pod, a single label will do if it matches correctly. However if you feel there could be other pods with the same label but with a different function then you could specify both the labels to ensure that the right pods are discovered by the replica set on creation.

If the labels match the replica set is created successfully it works the same for other objects like a service when a **service** is created it uses the selector defined in the service definition file to match the labels set on the pods in the replica set definition file.

![Diagram](images/image372.png)

```yaml
For services
 ```
  apiVersion: v1
  kind: Service
  metadata:
   name: my-service
  spec:
   selector:
     app: App1
   ports:
   - protocol: TCP
     port: 80
     targetPort: 9376 
   ```
```

![Diagram](images/image169.png)

Finally let’s look at annotations. While labels and selectors are used to group and select objects, annotations

are used to record other details for informatory purposes. For example tool details like **name, version build** information etc or contact details, **phone numbers, email-ids** etc, that may be used for some kind of integration purpose.

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: simple-webapp
  labels:
    app: App1
    function: Front-end
  annotations:
     buildversion: 1.34
spec:
 replicas: 3
 selector:
   matchLabels:
    app: App1
template:
  metadata:
    labels:
      app: App1
      function: Front-end
  spec:
    containers:
    - name: simple-webapp
      image: simple-webapp  
```

![Diagram](images/image134.png)

#### Practice Test Commands

```bash
$ kubectl get pods --selector env=dev
$ kubectl get pods --selector bu=finance
$ kubectl get all --selector env=prod
$ kubectl get all --selector env=prod,bu=finance,tier=frontend
```

### Taints and Tolerations

Will discuss about the pod to node relationship and how you can restrict what pods are placed on what nodes. **Taints and Tolerations are used to set restrictions on what pods can be scheduled on a node.** 

- Only pods which are tolerant to the particular taint on a node will get scheduled on that node.

So we will try to understand what they are using an analogy of a “bug approaching a person” 

To prevent the bug from landing on the person we spray the person with a repellent spray or **a taint** as we will call it. The bug is intolerant to the smell so on approaching the person the taint applied on the person throws the bug off, however there could be other bugs that are tolerant to the smell and so the taint doesn't really affect them. So they end up landing on the person. So there are two things that decide if a bug can land on a person. 

- *First the taint on the person.**

- *And second the bugs toleration level to that particular taint.**

![Diagram](images/image129.png)

![Diagram](images/image45.png)

Getting back to **Kubernetes**, the person is a node and the bugs are pods. Now taints and toleration have nothing to do with security or intrusion on the Cluster. Taints and toleration are used to set restrictions on what pods can be scheduled on a node.Let us start with a simple cluster with three worker nodes the nodes are named **one two** and **three**. We also have a set of PODs to be deployed on the nodes Let's call them A B C and D. → When the pods are created kubernetes  scheduler tries to place these pods on the available worker nodes. As of now there are no restrictions or limitations and as such the scheduler places the pods across all of the nodes to balance them out equally.  Now let us assume that we have dedicated resources on node1 for a particular use case or application so we would like only those **pods** that belong/matching to this application to be placed on node1. First we prevent all pods from being placed on the node by placing a taint on the node.Let's call it **blue** By default Pods have no tolerations which means unless specified otherwise none of the pods can tolerate any taint. So in this case none of the Pods can be placed on node1 as none of them can tolerate the taint blue. → This solves half of our requirement that no unwanted PODs are going to be placed on this node. The other half is to enable certain PODs to be placed on this node. For this we must specify which PODs are tolerant to this particular **taint(blue).** In our case we would like to allow only POD D to be placed on this node so we add a toleration to **POD D.**  **POD D** is now tolerant to **blue** so when the scheduler tries to place this POD on Node1 iit goes through. Node1 can now only accept PODs  that can tolerate the taint Blue. So with all the Taints and toleration in place this is how the PODs would be scheduled. 

- The scheduler tries to place POD A on node1 but due to the taint it is thrown off and it goes to node2

- The scheduler then tries to place POD B on node1 but again due to the taint it is thrown off and is placed on Node 3 which happens to be the next free node.

- The scheduler then tries to place POD C to the Node One it is thrown off again and ends up on Node2.  Finally the scheduler tries to place POD D on Node1 since the POD is tolerant to Node1 it goes through

![Diagram](images/image303.png)

***So remember Taints are set on nodes and toleration are set on pods.***  

**So How we do this ?**  Use the kubectl taint nodes command to taint a node, specify the name of the node to taint followed by the taint  itself which is a key value pair. `Adding Taint to Nodes` 

```bash
$ kubectl taint nodes <node-name> key=value:taint-effect
Example
$ kubectl taint nodes node1 app=blue
```

The taint effect defines what would happen to the pods If they do not tolerate the taint. There are three taint effects 

- *Noschedule** which means the PODs will not be scheduled on the node which is what we have been discussing.`Example``$ kubectl taint nodes node1 app=blue:NoSchedule`

- *PreferNoSchedule** which means the system will try to avoid placing a pod on the node but that is not guaranteed.

- *NoExecute**: Which means that new PODs  will not be scheduled on the node and existing PODs on the node if any will be evicted if they do not tolerate the taint. These PODs may have been scheduled on the node prior to the creation of taint. `kubectl taint node node1 app=blue:NoExecute`

![Diagram](images/image179.png)

#### Adding Tolerations to POD

Tolerations are added to PODs, to add a toleration to a pod First pull up the pod definition file, in the spec section of the pod definition file add a section called tolerations move the same values used to while creating the taint under this section. The key is app operator is equal value is blue and the effect is NoSchedule And remember all of these values need to be encoded in double codes. `apiVersion: v1`

```yaml
kind: Pod
metadata:
 name: myapp-pod
spec:
 containers:
 - name: nginx-container
   image: nginx
 tolerations:
 - key: "app"
   operator: "Equal"
   value: "blue"
   effect: "NoSchedule" 
```

When the pods are now created or updated with the new toleration they are either not scheduled on nodes

or evicted from the existing nodes depending on the effect set 

Let us try to understand the **NoExecute** taint effect in a bit more depth. 

In this example we have three nodes running some workload. We do not have any taints or toleration at this point so they are scheduled this way.  

![Diagram](images/image24.png)

We then decided to dedicate Node One for a special application and as such we Tainted the node with the

application name and add a toleration to the POD that belongs to the application which happens to be 

**POD D** in this case.  While Tainting the node we set the taint effect to NoExecute and as such once Taint on the Node takes effect it evokes **POD C** from the nodem which simply means that the POD is killed.

The POD D continues to run on the node as it has a toleration to the the taint **Blue** 

![Diagram](images/image309.png)

![Diagram](images/image141.png)

Going  back to our original scenario where we have taints and tolerations configured, remember Taints and toleration are only meant to restrict nodes from accepting certain PODs.  In this case Node One can only accept **POD D** but it does not guarantee that POD D will always be placed on Node1. Since there are no Taints or restrictions applied on the other two nodes POD D may very well be placed on any of the other two nodes so remember taints and toleration does not tell the POD to go to a particular node. Instead it tells the node to only accept PODs with certain toleration. 

If your requirement is to restrict a POD to certain nodes it is achieved through another concept called **Asknode** affinity.  Which will be discussed in the next lecture.Finally, while we're on this topic let us also take a look at an interesting fact. So far we have only been referring to the worker nodes, but we also have master nodes in the cluster which is technically just another node that has all the capabilities of hosting a POD. Plus it runs all the management software. Now I'm not sure if you noticed the scheduler does not schedule any POD on the master node.**Why is that ?** When the kubernetes cluster is first set up a taint is set on the master node automatically that prevents any PODs from being scheduled on this node. You can see this as well as modify his behavior if required. However, a best practice is to not deploy application workloads on a master server. 

To see this taint run a # `kubectl describe node kubemaser | grep Taint` and look for the taint section You will CA taint set to not schedule any PODs on the master node.

**Do any taints exist on node01 node?** 

```bash
# kubectl describe node node01 | grep Taint
Taints:         <none>
```

Create a taint on node01 with key of spray, value of mortein and effect of NoSchedule 

```yaml
# kubectl taint nodes node01 spray=mortein:NoSchedule
apiVersion: v1
kind: Pod
metadata:
     name: mosquito
     label:
        app: my-app
        tier: front-end
spec:
     containers:
     - name: nginx 
 image: nginx 
```

To remove taint from a node. 

```bash
# kubectl taint nodes controlplane node-role.kubernetes.io/master:NoSchedule-
node/controlplane untainted
```

### Node Selectors

You have a three node cluster of which two are smaller nodes with lower hardware resources and one of

them is a larger node configured with higher resources, you have different kinds of workloads running

in your cluster. You would like to dedicate the data processing workloads that require higher horsepower to the larger node as that is the only node that will not run out of resources in case the job demands extra resources.

However, in the current default setup, any pods can go to any nodes. 

![Diagram](images/image191.png)

![Diagram](images/image345.png)

So **Pod C** in this case may very well end up on nodes two or three which is not desired. To solve this we can set a limitation on the pods so that they only run on particular nodes. 

**There are two ways to do this.**

- The first is using NodeSelectors which is the simple and easier method.

For this we look at the pod definition file we created earlier. This file has a simple definition to create a pod with a data processing image.To limit this pod to run on the larger node We add a new property called `nodeSelector` to the spec section and specify the size as large. But wait a minute !! **Where did the size large come from and how does Kubernetes know which is the large node?** The key value pair of size and large are in fact labels assigned to the nodes. The scheduler uses these labels to match and identify the right node to place the pods on. Labels and selectors are a topic we have seen many times throughout this Kubernetes course such as with Services, ReplicaSets and Deployments. To use labels in a known selector like this you must have first labelled your nodes prior to creating this pod. So  let us go back and see how we can label the nodes. To label a node use below the command 

```bash
Syntax$ kubectl label nodes <node-name> <label-key>=<label-value>
Example$ kubectl label nodes node-1 size=Large
```

Now that we have labeled the node we can get back to creating the pod this time with the node selector

set to a size of large.

```yaml
apiVersion: v1
kind: Pod
metadata:
 name: myapp-pod
spec:
 containers:
 - name: data-processor
   image: data-processor
 nodeSelector:
   size: Large
$ kubectl create -f pod-definition.yml
```

When the pod is now created it is placed on Node01 as desired. nodeSelector served our purpose but it has **limitations**. We used a single label and selector to achieve our goal here. But what if our requirement is much more complex. For example:We would like to say something like place the pod on a large or medium node or something like place the pod on any nodes that are not small. You **cannot** achieve this using NodeSelectors for this node affinity and anti affinity features were introduced and we will look at that next.

### Node Affinity

![Diagram](images/image366.png)

The primary purpose of node affinity feature is to ensure that pods are hosted on particular nodes. In this case to ensure the large data processing pod ends up on node01. In the previous lecture we did this easily using Node Selectors, we discussed that you cannot provide advanced expressions like **or/not** with node selectors, the node affinity feature provides us with advanced capabilities to limit pod placement on specific nodes. With great power comes great complexity.So the simple node selector specification will now look like this with node affinity. although both does exactly the same thing, “place the pod on the large node”.

```yaml
Node Selector ---
apiVersion: v1
kind: Pod
metadata:
 name: myapp-pod
spec:
 containers:
 - name: data-processor
   image: data-processor
 nodeSelector:
  size: Large


Node Affinity
---
apiVersion: v1
kind: Pod
metadata:
 name: myapp-pod
spec:
 containers:
 - name: data-processor
   image: data-processor
 affinity:
   nodeAffinity:
     requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: size
            operator: In
            values: 
```

- `- Large`Let us look at it a bit closer, under spec you have `affinity` and then `nodeAffinity` under that, and then you have a property that looks like a sentence called **required during scheduling ignored during execution**(`requiredDuringSchedulingIgnoredDuringExecution)` no description needed for that and then you have the node selector terms that is an **array** and that is where you will specify the key and value pairs.The key value pairs are in the form **key**, `operator` **and value** where the operator is `In`, the `In` operator ensures that the pod will be placed on a node whose label size has any value in the list of values specified here in this case it is just one called **large**. If you think your POD could be placed on a large or a medium node you could simply add the value to the list of values like this

```yaml
apiVersion: v1
kind: Pod
metadata:
 name: myapp-pod
spec:
 containers:
 - name: data-processor
   image: data-processor
 affinity:
   nodeAffinity:
     requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: size
            operator: In 
            values: 
            - Large
            - Medium
or         
           operator: NotIn 
 values: 
       - Small
```

you could use the `NotIn` operator to say something like size not in small where node affinity will match the node with a size not set to small. 

We know that we have only set the label size to large and medium nodes; the smaller nodes don't even have the labels set. So we don't really have to even check the value of the label as long as we are sure we don't set a label size to the smaller nodes using the `Exists` operator, will give us the same result.

```yaml
apiVersion: v1
kind: Pod
metadata:
 name: myapp-pod
spec:
 containers:
 - name: data-processor
   image: data-processor
 affinity:
   nodeAffinity:
     requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: size
            operator: Exists
```

The “`Exists``”` operator will simply check if the label size exists on the nodes and you don't need the values section for that as it does not compare the values.

There are a number of other operators as well. Check the documentation for specific details.Now we understand all of this and we're comfortable with creating a pod with specific affinity rules, when the pods are created. These rules are considered and the pods are placed onto the right nodes.

**But what if node affinity could not match a node with a given expression ?** 

In this case what if there are no nodes with a label called size, say we had the labels and the pods are scheduled. **What if someone changes the label on the node at a future point in time**? **Will the pod continue to stay on the Node ?**All of this is answered by the long sentence like property under node affinity, which happens to be the type of node affinity, the type of node affinity defines the behavior of the scheduler with respect to node affinity and the stages in the lifecycle of the pod. 

There are currently two types of node affinity available, 

`requiredDuringSchedulingIgnoredDuringExecution` and  `preferredDuringSchedulingIgnoredDuringExecution` 

![Diagram](images/image229.png)

and there are two are additional types of node affinity “**planned**” We will now break this down to understand further. We will start by looking at the two available affinity types. There are two states in the lifecycle of a pod when considering node affinity 

- *during scheduling**

- *during execution**

**During scheduling** is the state where a pod does not exist and is created for the first time. We have no doubt that when a pod is first created the affinity rules specified are considered to place the pods on the right node. 

**Now what if the nodes with matching labels are not available?** 

For example we forgot to label the node as large. That is where the **type of node affinity** used comes into play. 

- If you select the required type which is the first one the scheduler will mandate that the pod be placed on a node with a given affinity rules, if it cannot find one the pod will not be scheduled.This type will be used in cases where the placement of the pod is crucial. If a matching node does not exist the pod will not be scheduled.

- But let's say the pod placement is less important than running the workload itself. In that case you could set it to **preferred** and in cases where a matching node is not found. The scheduler will simply ignore node affinity rules and place the POD on any available node. This is a way of telling the scheduler  “*hey try your best to place the pod on a matching node but if you really cannot find one just place it anywhere*”.

The second part of the property or the other state is during execution. During execution is the state where a POD has been running and a change is made in the environment that affects node affinity such as a change in the label of a node.

For example say an administrator removed the label we said earlier called “size” equals large from the node. **Now what would happen to the pods that are running on the Node?****→** As you can see the two types of node affinity available today have this value set to ignored which means pods will continue to run and any changes in node affinity will not impact them once they are scheduled.

The two new types expected in the future only have a difference in the during execution phase a new option called `requiredDuringExecution` is introduced which will evict any pods that are running on nodes that do not meet affinity rules. In the earlier example, a pod running on the large node will be evicted or terminated if the label large is removed from the node. 

#### Test Solutions

Run the command `'kubectl describe node node01`' and count the number of labels under **Labels Section**.

```yaml
kubectl label nodes node01 color=Blue
apiVersion: apps/v1kind: Deploymentmetadata:    name: blue    labels:app: nginxspec:  replicas: 3  selector:     matchLabels: app: nginx  template:    metadata:      labels:  app:nginx    spec:      containers:- name: nginx  image: nginx
```

### Taints and Tolerations vs Node Affinity

![Diagram](images/image321.png)

Now that we have learned about Taints and toleration and node affinity, let us tie together the two concepts through a fun exercise.

We have three nodes and three PODs, each in three colors, blue, red and green. The ultimate aim is to place the blue POD in the blue node, the red POD in the red node and likewise for Green. We are sharing the same kubernetes cluster with other teams.So there are other PODs in the cluster as well as other nodes. We do not want any other pod to be placed on our node. Neither do we want our pods to be placed on their nodes.

Let us first try to solve this problem using Taints and Toleration. We apply a taint to the nodes, marking them with their colors **blue, red and green** and we then set a tolerance on the PODs to tolerate the respective colors.When the PODs are now created, the nodes ensure they only accept the PODs with the right toleration. So the green POD ends up on the green node and the blue POD ends up on the blue node. However, Taints and toleration does not guarantee that the PODs will only prefer these nodes. So the red node ends up on one of the other nodes that do not have a taint or toleration set. This is not desired. 

Let us try to solve the same problem with node affinity. With node affinity, we first labeled the nodes with their respective colors blue, red and green. We then set node selectors on the POD to tie the POD to the nodes.

As such, the pods end up on the right node. However, that does not guarantee that other PODs are not placed on these nodes. In this case, there is a chance that one of the other PODs may end up on our node. This is not something we desired. As such a combination of Taints and toleration and nodeAffinity rules can be used together to completely dedicate nodes for specific PODs. 

We first used Taints and tolerations to prevent other PODs from being placed on our nodes, and then we used node affinity to prevent our PODs from being placed on their nodes.

### Resource Limits

Let's look at a three node Kubernetes cluster. Each node has a set of **CPU, memory and disk** resources available, every POD consumes a set of resources, in this case, two CPUs, one memory and some disk space.

![Diagram](images/image56.png)

Whenever a pod is placed on a node, it consumes resources available to that node. As we have discussed before, it is the **Kubernetes scheduler** that decides which node a POD goes to. The scheduler takes into consideration the amount of resources required by a POD and those available on the nodes. 

![Diagram](images/image315.png)

In this case, the scheduler schedules a new POD on node two. If the node has no sufficient resources, the scheduler avoids placing the POD on that node, instead places the POD on one in which sufficient resources are available. If there is no sufficient resources available on any of the nodes, kubernetes hold back scheduling the POD, you will see the POD in a **pending state.**

![Diagram](images/image283.png)

![Diagram](images/image370.png)

If you look at the events, you will see the reason, **insufficient CPU.**

Let us now focus on the resource requirements for each POD. 

What are these blocks and what are their values? 

![Diagram](images/image2.png)

By default kubernetes assumes that a POD or a container within a POD **requires 0.5 CPU and 256 mebibytes of memory.** This is known as the **resource request** for a container, the minimum amount of CPU or memory requested by the container. When the scheduler tries to place the POD on a node, it uses these numbers to identify a node which has a sufficient amount of resources available. 

Now, if you know that your application will need more than this, you can modify these values by specifying them in your POD or  deployment definition files. 

```yaml
pod-definition.yaml
apiVersion: v1
kind: Pod
metadata:
  name: simple-webapp-color
  labels:
    name: simple-webapp-color
spec:
 containers:
 - name: simple-webapp-color
   image: simple-webapp-color
   ports:
     - containerPort:  8080
   resources:
     requests:
       memory: "1Gi"
       cpu: "1"
```

![Diagram](images/image358.png)

In the simple pod definition file, add a section called `resources` `under spec`, under which add requests and specify the new values for memory and CPU usage. In this case, It set it to 1GB of memory and one count of CPU.

**So what does one count of C.P.U really mean?** It doesn't have to be in the increment of .5 you can specify any value as low as 0.1, 0.1 C.P.U can also be expressed as one hundred M where M stands for milli. You can go as low as one M, but not lower than that.One count of CPU is equivalent to one CPU, i.e CPU in AWS or 1 core in GCP or 1 core in Azure or 1 Hyperthread.

You could request a higher number of CPU's for the container, provided your nodes are sufficiently funded.

![Diagram](images/image272.png)

Similarly with memory, you could specify 256Mi  or specify the same value in memory(MEM) like this 

![Diagram](images/image225.png)

Let's now look at a container running on a node. 

In the docker world a docker container has no limit to the resources it can consume on a node. Say a container starts with one vCPU on a node It can go up and consume as much resource as it requires, suffocating the native processes on the node or other containers of resources. However, you can set a limit for the resource usage on these PODs. By default, kubernetes sets a limit of one vCPU to containers. So if you do not specify explicitly, a container will be limited to consume only one vCPU from the node.The same goes with memory.By default, kubernetes sets a limit of 512Mi on containers. If you don't like the default limit, you can change them by adding a limits section under the resources section In your POD definition file. Specify new limits for the memory and CPU like this.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: simple-webapp-color
  labels:
    name: simple-webapp-color
spec:
 containers:
 - name: simple-webapp-color
   image: simple-webapp-color
   ports:
    - containerPort:  8080
   resources:
     requests:
      memory: "1Gi"
      cpu: "1"
     limits:
       memory: "2Gi"
       cpu: "2"
```

When the pod is created, kubernetes sets new limits for the container. Remember that the limits and requests are set for each container within the pod. **So what happens when a pod tries to exceed resources beyond its specified limit?**

In case of CPU, kubernetes throttles the CPU so that it does not go beyond the specified limit. A container cannot use more CPU resources than its limit. However, this is not the case with the memory.A container can use more memory resources than its limit. So if a pod tries to consume more memory than its limit constantly, the POD will be terminated.

#### Additional Notes on default resource requirements

As said in the previous lecture, – “When a pod is created the containers are assigned a default CPU request of .5 and memory of 256Mi”. For the POD to pick up those defaults you must have first set those as default values for request and limit by creating a LimitRange in that namespace.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: mem-limit-range
spec:
  limits:
  - default:
      memory: 512Mi
    defaultRequest:
      memory: 256Mi
    type: Container
apiVersion: v1
kind: LimitRange
metadata:
  name: cpu-limit-range
spec:
  limits:
  - default:
      cpu: 1
    defaultRequest:
      cpu: 0.5
    type: Container
```

References 

#### Note on editing PODs and Deployments

**Edit a POD**

Remember, you CANNOT edit specifications of an existing POD other than the below.

- spec.containers[*].image

- spec.initContainers[*].image

- spec.activeDeadlineSeconds

- spec.tolerations

For example you cannot edit the environment variables, service accounts, resource limits (all of which we will discuss later) of a running pod. But if you really want to, you have 2 options:

1. Run the `kubectl edit pod <pod name>` command.  This will open the pod specification in an editor (vi editor). Then edit the required properties. When you try to save it, you will be denied. This is because you are attempting to edit a field on the pod that is not editable.

![Diagram](images/image155.png)

![Diagram](images/image46.png)

A copy of the file with your changes is saved in a temporary location as shown above.

You can then delete the existing pod by running the command:

```bash
kubectl delete pod webapp
```

Then create a new pod with your changes using the temporary file

```bash
kubectl create -f /tmp/kubectl-edit-ccvrq.yaml
```

2. The second option is to extract the pod definition in YAML format to a file using the command

```bash
kubectl get pod webapp -o yaml > my-new-pod.yaml
```

Then make the changes to the exported file using an editor (vi editor). Save the changes

```text
vi my-new-pod.yaml
```

Then delete the existing pod

```bash
kubectl delete pod webapp
```

Then create a new pod with the edited file

```bash
kubectl create -f my-new-pod.yaml
```

#### Edit Deployments

With Deployments you can easily edit any field/property of the POD template. Since the pod template is a child of the deployment specification,  with every change the deployment will automatically delete and create a new pod with the new changes. So if you are asked to edit a property of a POD part of a deployment you may do that simply by running the command

```bash
kubectl edit deployment my-deploymentNote: The status OOMKilled indicates that it is failing because the pod ran out of memory. Identify the memory limit set on the POD.
```

### Demon sets

So far, we have deployed various PODs on different nodes in our cluster, with the help of ReplicaSets

and deployments, we made sure multiple copies of our applications are made available across various

different worker nodes. 

DemonSets are like ReplicaSets, as in it helps you deploy multiple instances of pods, **but it runs one copy of your pod on each node in your cluster.** Whenever a new node is added to the cluster, a replica of the pod is automatically added to that node. And when a node is removed, the pod is automatically removed. **The demon set ensures that one copy of the pod is always present in all nodes in the cluster.** 

![Diagram](images/image297.png)

So what are some **use cases** of demon sets?  Say you would like to deploy a monitoring agent or log collector on each of your nodes in the cluster so you can monitor your cluster better. A demon set is perfect for that, as it can deploy your monitoring agent in the form of a pod in all the nodes in your cluster. Then you don't have to worry about adding or removing monitoring agents from these nodes when there are changes in your cluster, as the demon set will take care of that for you. 

Earlier while discussing the architecture, we learned that one of the worker node components that is required on every node in the cluster is a “Kube proxy” That is one good use case of demon sets. The Kube proxy component can be deployed as a demon set in the cluster. Another use case is for networking, Networking solutions like weavenet require an agent to be deployed on each node in the cluster. We will discuss networking concepts in much more detail later during this course. → Creating a demon set is similar to the replicaSet creation process. It has nested part specification under the template section and selectors to link the demon set to the PODs →  A demon set definition file has a similar structure. For DaemonSets, we start with apiVersion: `apps/v1`, Kind as **DaemonSets** instead of **ReplicaSet**, **metadata** and **spec**.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: monitoring-daemon
  labels:
    app: nginx
spec:
  selector:
    matchLabels:
      app: monitoring-agent
  template:
    metadata:
     labels:
       app: monitoring-agent
    spec:
      containers:
      - name: monitoring-agent
        image: monitoring-agent
$ kubectl create -f daemon-set-definition.yaml
```

Under spec you have a selector and a POD specification template. Ensure the labels in The Selecter matches the ones in the pod template once ready, create the demonset using the kubectl  create command.

To view the created  DemonSet run to `kubectl` `get demonset` command and of course, to view more details use kubectl, describe demons that command.

```bash
$ kubectl get deamonsets  $ kubectl describe daemonsets monitoring-daemon
```

**So how does it work?****How does it schedule pods on each node and how does it ensure that every node has a pod?** **If you were asked to schedule a POD on each node in the cluster, how would you do it?**

In one of the previous lectures in this section, we discussed that we could set the `nodeName` property on the pod to bypass the scheduler and get the POD placed on a node directly. So that's one approach.On each POD, set the nodeName, property and its specification before it is created.And when they are created, they automatically land on the respective nodes.  

So that's how it used to be until kubernetes version v1.12, but from version v1.12 onwards, the demonSet uses the default scheduler and node affinity rules that we learned in one of the previous lectures to schedule PODs on nodes.

#### Practice Test

```bash
kubectl get daemonsets --all-namespaces 
kubectl describe daemonsets kube-flannel-ds -n kube-system
kubectl describe daemonsets kube-flannel-ds -n kube-system
kubectl create deployment elasticsearch --image=k8s.gcr.io/fluentd-elasticsearch:1.20 -n kube-system --dry-run=client -o yaml > fluentd.yaml
```

Next, remove the replicas, strategy and status fields from the YAML file using a text editor. Also, change the kind from Deployment to DaemonSet.

```bash
Finally, create the Daemonset by running kubectl create -f fluentd.yaml
```

### Static Pods

![Diagram](images/image39.png)

In this course we talked about the Architecture and how the kubelet functions as one of the many control plane components in Kubernetes. The kubelet relies on the kube-apiserver for instructions on what PODs to load on its node, which was based on a decision made by the kube-scheduler which was stored in the ETCD datastore. 

**What if there was no kube-apiserver, and kube-scheduler and no controllers and no ETCD cluster.**

**What if there was no master at all.**

**What if there were no other nodes?**

**What if you're all alone in the sea by yourself. Not part of any cluster.**

**Is there anything that the kubelet can do as the captain on the ship?** 

**Can it operate as an independent node?**

**If so, who would provide the instructions required to create PODs?**

Well, the kubelet can manage a node independently. On the host, we have the kubelet installed and of course we have Docker as well to run containers. There is no Kubernetes cluster. So there are no Kube API servers or anything like that. The one thing that the kubelet knows to do is create PODs but we don’t have an API server here to provide POD details. By now we know that to create a POD you need the details of the POD in a POD definition file.  But how do you provide a pod definition file to the kubelet without a kube-api server? 

You can configure the kubelet to read the pod definition files from a directory on the server designated

to store information about pods. Place the POD definition files in this directory, the Kubelet periodically checks this directory for files, reads these files and creates pods on the host.

Not only does it create the pod it can ensure that the pod stays alive. If the application crashes, the kubelet attempts to restart it. If you make a change to any of the files within this directory, the kubelet recreates the pod for those changes to take effect.If you remove a file from this directory the POD is deleted automatically.

So these PODs that are created by the kubelet on its own without the intervention from the API server 

or rest of the kubernetes cluster components are known as Static PODs. 

Remember you can only create PODs this way, you cannot create ReplicaSets or deployments or services by placing a definition file in the designated directory.They are all concepts part of the whole Kubernetes architecture, that requires other cluster control plane components like the replication and deployment controllers etc. The kubelet works at a POD level and can only understand PODs. Which is why it is able to create static pods this way.

So what is that designated folder  and how do you configure it?

It could be any directory on the host. And the location of that directory is passed in to the kubelet as an option while running the service.

![Diagram](images/image421.png)

The option is `--pod-manifest-path` and here it is set to `/etc/Kubernetes/manifests`. There is also another way to configure this, instead of specifying the option directly in the `kubelet.service` file, you could provide a path to another config file using the config option, and define the directory path as `staticPodPath` in that file. 

![Diagram](images/image29.png)

Clusters set up by the kubeadm tool use this approach. If you are inspecting an existing cluster, you should inspect this option of the kubelet to identify the path to the directory. You will then know where to place the definition file for your static pods.

So keep this in mind when you go through the labs. You should know to view and configure this option irrespective of the method used to set up the cluster, first check the option `--pod-manifest-path` in the kubelet service file if it's not there then look for the `--config` option and identify the file used as the config file and then within the config file(eg: `kubeconfig.yaml`) look for these static pod path option. Either of these should give you the right path.

Once the static PODs are created you can view them by running the `docker ps` command. So why not the kubectl command as we have been doing so far, remember we don’t have the rest of the Kubernetes cluster. Kubectl utility works with the kube-apiserver. Since we don’t have an API server now, there is no kubectl utility. which is why we're using the docker command.

**So then how does it work when the node is part of a cluster?** 

![Diagram](images/image120.png)

**When there is an API server requesting the Kubelet to create pods. Can the kubelet create both kinds of PODs at the same time?** Well, the way the kubelet works is it can take in requests for creating PODs from different inputs.  1. The first is through the POD definition files from the static pods folder,as we just saw.  2. The second, is through an HTTP API endpoint. And that is how the kube-apiserver provides input to the kubelet. 

The kubelet can create both kinds of PODs – the static pods and the ones from the api server - at the same time.

**Well, in that case is the API server aware of the static pods created by the kubelet?**Yes it is. If you run the kubectl get pods command on the master node, the static pods will be listed as any other pod. 

![Diagram](images/image88.png)

Well how is that happening? **When the kubelet creates a static pod, if it is part of a cluster, it also creates a mirror object in the kubeapi server.**What you see from the kube-apiserver is just a read only mirror of the pod. You can view details about the pod but you cannot edit or delete it like the usual PODs. You can only delete them by modifying the files from the nodes manifest folder.*Note that the name of the POD is automatically appended with the node name, In this case node01.* 

**So then why would you want to use Static PODs?**Since static pods are not dependent on the Kubernetes control plane, you can use static pods to deploy the control plane components itself as pods on a node. Start by installing a kubelet on all the master nodes Then create pod definition files that use Docker images of the various control plane components such as the api server, controller, etcd etc.Place the definition files in the designated manifests folder. And kubelet takes care of deploying the control plane components themselves as PODs on the cluster. This way you don't have to download the binaries, configure services or worry about the services crashing.

![Diagram](images/image380.png)

If any of these services were to crash since it's a static pod it will automatically be restarted by the kubelet. Neat and simple. **That’s how the** **kubeadmin** **tool set’s up a Kubernetes cluster.**

Which is why when you list the pods in the kube-system namespace, you see the control plane components as PODs in a cluster setup by the kubeadmin tool.We will explore that setup in the upcoming practice test. 

Before I let you go, one question that I get often is about the difference between Static PODs and DaemonSets.  

DaemonSets as we saw earlier are used to ensure one instance of an application is available on all nodes in the cluster. It is handled by a daemonset controller through the kube-api server. Whereas static pods, as we saw in this lecture, are created directly by the kubelet without any interference from the kube-api server or rest of the Kubernetes control plane components. Static pods can be used to deploy the Kubernetes control plane components itself. Both static pods and pods created by daemonsets are ignored by the kube-scheduler. The kube-scheduler has no effect on these pods. 

PRACTICE TEST - STATIC PODS 

```bash
kubectl get pods  --all-namespaces 
```

To identify static pods look for POD names appended by node name, like controlplane or node-01 etc… 

```text
/etc/kubernetes/manifests/kube-apiserver.yaml -- location where path to folder of static manifests are located 
```

### Multiple Schedulers

In this lecture we'll look at the different ways of manually scheduling a POD on a node. 

We will also look at how to view scheduler related events. We have seen how the default-scheduler works in a kubernetes environment in the previous lectures. It has an algorithm that distributes pods across nodes evenly as well as takes into consideration the various conditions we specify through taints & tolerations and node affinity etc. 

**But what if none of these satisfies your needs?** 

Say you have a specific application that requires its components to be placed on nodes after performing some additional checks. So you decide to have your own scheduling algorithm to place pods on nodes, so that you can add your own custom conditions and checks in it. Kubernetes is highly extensible You can write your own kubernetes scheduler program, package it and deploy it as the default scheduler or as an additional scheduler in the kubernetes cluster. That way all of the other applications can go through the default scheduler, however one specific application can use your custom scheduler. Your kubernetes cluster can have multiple schedulers at the same time. 

When creating a POD or a Deployment you can instruct kubernetes to have the POD scheduled by a specific scheduler. Earlier we saw how to deploy the kube-scheduler. We download the kube-scheduler binary and run it as a service with a set of options. One of the options is the scheduler name. If not specified It assumes the name of default scheduler. This kube-scheduler is the default scheduler.

![Diagram](images/image415.png)

To deploy an additional scheduler, You can use the same kube-scheduler binary or use one that you might have built for yourself, which makes more sense.  

![Diagram](images/image349.png)

In this case we are going to use the same binary to deploy the additional scheduler. This time we set the scheduler name to a custom name.  This is important to differentiate the two schedulers and this is the name that we will be specifying in the pod definition file later on.  Let’s take a look at how it works with the kubeadm tool. The kubeadm tool deploys the scheduler as a POD, you can find the definition file it uses under the manifests folder (Removed all the other details from the file so we can focus on the key parts. )

```bash
$ kubectl create -f my-custom-scheduler.yaml
```

To list the scheduler pods 

```bash
$ kubectl get pods -n kube-system
```

The command section has the command and associated options to start the scheduler.  We can create a custom scheduler by making a copy of the same file, and by changing the name of the scheduler. We can set the name of the pod to **my-custom-scheduler** and we add a new option to the scheduler command to set a custom name for the scheduler.  Finally an important option to look here is the --`leader-elect` option. The --`leader-elect` option is used when you have multiple copies of the scheduler running on different master nodes, in a High Availability setup where you have multiple master nodes with the kube-scheduler process running on both of them.

If multiple copies of the same scheduler are running on different nodes only one can be active at a time.

That’s where the `leader-elect` option helps in choosing a leader who will lead scheduling activities. We will discuss more about HA setup in another section, but for now I wanted to point out that, to get multiple schedulers working you must either set the `leader-elect` option to false, in case where you don’t have multiple masters.  In case you do have multiple masters, you can pass in an additional parameter to set a lock object name. This is to differentiate the new custom scheduler from the default during the leader election process. Once done, create the pod using the `kubectl create command`. Run the get pods command in the kube-system namespace and look for the new custom scheduler. 

Make sure it's in a running state. The next step is to configure a new POD or a deployment to use the new scheduler. In the Pod specification file. add a new field called `schedulerName` and specify the name of the new scheduler.

### Use the Custom Scheduler

```yaml
Create a pod definition file and add new section called schedulerName and specify the name of the new schedulerapiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - image: nginx
    name: nginx
  schedulerName: my-custom-scheduler
$ kubectl get events
```

![Diagram](images/image184.png)

```bash
To create a pod definition$ kubectl create -f pod-definition.yaml
To list pods$ kubectl get pods
```

This way when the pod is created, the right scheduler picks it up to schedule. Create the pod using the kubectl create command. If the scheduler was not configured correctly, then the pod will continue to remain in a Pending state. If everything is good, then the pod will be in a Running state. 

So how do you know which scheduler picked it up? View the events using the kubectl get events command. This lists all the events in the current namespace.Look for the Scheduled events. As you can see the source of the event is the custom scheduler we created.`To view events``$ kubectl get events`

![Diagram](images/image95.png)

And the message says successfully assigned default/nginx image. 

To view the logs of the scheduler,

```bash
To view scheduler logs
$ kubectl logs my-custom-scheduler -n kube-system
```

![Diagram](images/image419.png)

View the logs of the pod using the kubectl logs command. Specify the name of the scheduler the correct namespace.

```yaml
We have already created the ServiceAccount and ClusterRoleBinding that our custom scheduler will make use of.Checkout the following kubernetes objects:
ServiceAccount: my-scheduler (kube-system namespace)
ClusterRoleBinding: my-scheduler-as-kube-scheduler
ClusterRoleBinding: my-scheduler-as-volume-scheduler

ConfigMap
root@controlplane ~ ➜  cat my-scheduler-config.yaml
apiVersion: kubescheduler.config.k8s.io/v1beta2
kind: KubeSchedulerConfiguration
profiles:
  - schedulerName: my-scheduler
leaderElection:
  leaderElect: false
```

#### Configuring Kubernetes Scheduler

- We have seen different ways of configuring the scheduler.

- We saw how to setup scheduler manually and how kubeadm tool does it.

- We saw how to create additional schedulers and have PODs pick the new scheduler.

- We also looked at some of the options such as these scheduler name and pod name used while configuring the scheduler.

- Additional resources

---

### Topology Spread Constraints

Topology Spread Constraints control how Pods are distributed across failure domains such as regions, zones, nodes, and other user-defined topology domains. This achieves high availability and efficient resource utilization.

#### Core Fields

- **`maxSkew`**: The degree to which Pods may be unevenly distributed. Must be greater than zero.
- **`topologyKey`**: The key of node labels (e.g., `topology.kubernetes.io/zone`, `kubernetes.io/hostname`).
- **`whenUnsatisfiable`**:
  - `DoNotSchedule` (hard constraint): The scheduler will not schedule the Pod if it violates the skew.
  - `ScheduleAnyway` (soft constraint): The scheduler prioritizes nodes that minimize the skew but still schedules the Pod.
- **`labelSelector`**: Identifies matching Pods to count across topology domains.
- **`matchLabelKeys`** (Kubernetes 1.27+): List of Pod label keys to select the values dynamically from current pod (useful for rolling updates).

#### Topology Spread Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  labels:
    app: web
spec:
  replicas: 6
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: web
      containers:
      - name: nginx
        image: nginx:alpine
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
```

---

### PriorityClass & Pod Preemption

If a cluster runs out of compute resources, higher-priority Pods can preempt (evict) lower-priority Pods to free up capacity.

#### Defining a PriorityClass

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
globalDefault: false
description: "Mission-critical tier service priority class"
preemptionPolicy: PreemptLowerPriority # Or 'Never' for non-preempting priority
```

#### Assigning PriorityClass to a Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: critical-api-pod
spec:
  priorityClassName: high-priority
  containers:
  - name: api
    image: nginx:alpine
```

#### Key Rules:
- Higher `value` indicates higher priority.
- Built-in system priority classes: `system-cluster-critical` and `system-node-critical` (reserved values in billions).
- `preemptionPolicy: Never` allows Pods to jump the scheduling queue without evicting running lower-priority Pods.

---

### Pod Disruption Budgets (PDB)

A Pod Disruption Budget limits the number of Pods of a replicated application that can be simultaneously down from voluntary disruptions (e.g., `kubectl drain`, node maintenance, automated cluster autoscaler).

#### PDB Specifications

You can define either `minAvailable` or `maxUnavailable` (as an absolute integer or a percentage):

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-pdb
  namespace: default
spec:
  minAvailable: 2 # At least 2 pods must stay running during drain
  selector:
    matchLabels:
      app: web
```

Alternatively using `maxUnavailable`:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payments-pdb
  namespace: default
spec:
  maxUnavailable: "25%" # No more than 25% of replicas may be disrupted
  selector:
    matchLabels:
      app: payments
```

#### Useful Commands:
```bash
# List all active Pod Disruption Budgets
kubectl get pdb -A

# Inspect budget status (allowed disruptions, current healthy, desired healthy)
kubectl describe pdb web-pdb
```

---

### LimitRange (Container & Pod Resource Constraints)

While a `ResourceQuota` controls the total resource consumption of an entire namespace, a **`LimitRange`** sets boundaries and defaults on individual containers, pods, and PVCs within that namespace.

#### Core Capabilities
1. **Default Requests & Limits:** Automatically injected into pods that omit compute specifications by the `LimitRanger` admission controller.
2. **Min & Max Bounds:** Sets strict lower and upper bounds on container CPU and memory.
3. **Burst Ratio (`maxLimitRequestRatio`):** Caps `limit / request` ratio to prevent extreme overcommit.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: mem-limit-range
  namespace: default
spec:
  limits:
  - type: Container
    default: # Default limit
      cpu: 500m
      memory: 512Mi
    defaultRequest: # Default request
      cpu: 100m
      memory: 128Mi
    max:
      cpu: "2"
      memory: 1Gi
    min:
      cpu: 50m
      memory: 64Mi
    maxLimitRequestRatio:
      cpu: 4
      memory: 4
```
