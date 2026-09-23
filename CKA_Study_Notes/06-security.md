# 06. Security

## Security

### Kubernetes Security Primitives

The security primitives in Kubernetes. Kubernetes being the goto platform for hosting production grade applications, security is of prime concern. In this lecture we look at the various security primitives in Kubernetes at a high level before diving deeper into those in the upcoming lectures.

![Diagram](images/image154.png)

Let's begin with the host that formed the cluster itself. Of course all access to these hosts must be secured  1. Root access disabled, 2.  password based authentication disabled, and 3. Only SSH key based authentication to be made available and  4. Of course any other measures you need to take to secure your physical or virtual infrastructure that hosts kubernetes. Of course if that is compromised, everything is compromised.  Our focus in this lecture is more on Kubernetes related security. What are the risks and what measures do you need to take to secure the cluster. As we have seen already, the **kube-apiserver** is at the center of all operations within kubernetes. We interact with it through the **kubectl** utility or by accessing the API directly and through that you can perform almost any operation on the cluster. So that’s the first line of defense. Controlling access to the API server itself. We need to make two types of decisions: who can access the cluster and what can they do. Who can access the API server is defined by the Authentication mechanisms.  There are different ways that you can authenticate to the API server. Starting with user IDs and passwords stored in a static file ro tokens, certificates or even integration with external authentication providers like LDAP, okata etc.  So you cannot create users in k8s cluster or list the users, however in the case of service accounts k8s can manage them.  Finally for machines we create service accounts. We will look at these in more detail in the upcoming lectures. Once they gain access to the cluster, what they can do is defined by authorization mechanisms. Authorization is implemented using **Role Based Access Control,** where users are associated to groups with specific permissions. In addition there are other authorization modules like **Attribute based access control**, **Node Authorizers**, **webhooks** etc. Again we look at these in more detail in the upcoming lectures.

![Diagram](images/image255.png)

All **communication** with the cluster, between the various components such as the ETCD cluster, kube-controller-manager, scheduler, api server, as well as those running on the worker nodes such as the kubelet and and kubeproxy is secured using TLS Encryption. We have a section entirely for this where we discuss and practice how to set up the certificates between the various components. **What about communication between applications within the cluster. ?**By default all PODs can access all other PODs within the cluster. You can restrict access between them using Network Policies. We will look at how exactly that is done. Later in the network policy section. 

### Authentication

The kubernetes cluster consists of multiple nodes, physical or virtual, and various components that work together. If users like **administrators** that access the cluster to perform administrative tasks, the developers that access the cluster to test or deploy applications, we have end users who access the applications deployed on the cluster and we have third party applications accessing the cluster for integration purposes.

![Diagram](images/image14.png)

![Diagram](images/image192.png)

![Diagram](images/image189.png)

Throughout this section, we will discuss how to secure our cluster by securing the communication between internal components and securing management access to the cluster through authentication and authorization mechanisms. In this lecture our focus is on securing access to the kubernetes cluster with **authentication mechanisms.** So we talked about the different users that may be accessing the cluster, security of end users who access the applications deployed on the cluster is managed by the applications themselves internally.  So we will take them out of our discussion. Our focus is on users' access to the kubernetes cluster for administrative purposes.  So we are left with two types of users, **humans** such as the administrators & developers and **robots** such as other processors or services or applications that require access to the cluster. Kubernetes does not manage user accounts natively, it relies on an external source like a file with user details or certificates or a third party identity service like LDAP to manage these users.  And so you cannot create users in a kubernetes cluster or view the list of users like this. 

However, in case of service accounts, kubernetes can manage them. You can create and manage service accounts using the kubernetes API. We have a section on service accounts exclusively where we discuss and practice more about service accounts. For this lecture, we will focus on users in kubernetes, all user access is managed by the API server. Whether you're accessing the cluster through a kubectl tool or the API directly, all of these requests go through the kubeAPI server. The KubeAPI server authenticates the request before processing it. 

![Diagram](images/image392.png)

**So how does the API server authenticate?**There are different authentication mechanisms that can be configured. You can have a list of usernames and passwords in a static password file or usernames and tokens in a static token file, or you can authenticate using certificates. And another option is to connect to third party authentication protocols like LDAP and Kerberos, etc..

![Diagram](images/image394.png)

We will look at some of these next. Let's start with static password and token files as it is the easiest to understand. Let's start with the simplest form of authentication, you can create a list of users and their passwords in a csv file and use that as the source for user information. The file has three columns: password, username and user ID. We then pass the file name as an option to the KubeAPI server.

![Diagram](images/image424.png)

Remember the KubeAPI server service and the various options we looked at earlier in this course, that is where you must specify this option, you must then restart the kubeapi server for these options to take effect. If you set up your cluster using the kubeadm tool, then you must modify the kubeAPI server pod definition file. The kubeadm tool will automatically restart the kubeAPI server once you update this file.

![Diagram](images/image231.png)

To authenticate using the basic credentials while accessing the API server, specify the user and password in a curl command like this.`$ curl -v -k http://master-node-ip:6443/api/v1/pods -u "user1:password123"`

![Diagram](images/image300.png)

![Diagram](images/image59.png)

![Diagram](images/image266.png)

![Diagram](images/image291.png)

In The  CSV file with the user details that we saw, we can optionally have a fourth column with the group details to assign users to specific groups.  Similarly, instead of a static password file, you can have a static token file here instead of password, you specify a token, pass the token file as an option token auth file to the kubeAPI server while authenticating specified a token as an authorization bearer token to your request like this. That's it for this lecture. Remember that this authentication mechanism that stores usernames, passwords and tokens and clear text in a static file is not a recommended approach as it is insecure. But it is the easiest way to understand the basics of authentication and kubernetes going forward. We will look at other authentication mechanisms. I also want to point out that if you were trying this out in a kubeadm setup, you must also consider volume mounts to pass the auth file.  And remember to set up authorization for the new users.We will discuss about authorization later in this course in the upcoming lectures, we will discuss about certificate based authentication and how the various components within this cluster are secured  using certificates.

### Article On Setting Up Basic Authentication

#### Setup basic authentication on Kubernetes (Deprecated in 1.19)

```text
Note: This is not recommended in a production environment. This is only for learning purposes. Also note that this approach is deprecated in Kubernetes version 1.19 and is no longer available in later releases
```

Follow the below instructions to configure basic authentication in a kubeadm setup.

Create a file with user details locally at /tmp/users/user-details.csv

```text
# User File Contents
password123,user1,u0001
password123,user2,u0002
password123,user3,u0003
password123,user4,u0004
password123,user5,u0005
```

Edit the kube-apiserver static pod configured by kubeadm to pass in the user details. The file is located at `/etc/kubernetes/manifests/kube-apiserver.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: kube-apiserver
  namespace: kube-system
spec:
  containers:
  - command:
    - kube-apiserver
      <content-hidden>
    image: k8s.gcr.io/kube-apiserver-amd64:v1.11.3
    name: kube-apiserver
    volumeMounts:
    - mountPath: /tmp/users
      name: usr-details
      readOnly: true
  volumes:
  - hostPath:
      path: /tmp/users
      type: DirectoryOrCreate
    name: usr-details
```

**Modify the kube-apiserver startup options to include the basic-auth file**

```yaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  name: kube-apiserver
  namespace: kube-system
spec:
  containers:
  - command:
    - kube-apiserver
    - --authorization-mode=Node,RBAC
      <content-hidden>
    - --basic-auth-file=/tmp/users/user-details.csv
```

**Create the necessary roles and role bindings for these users:**

```yaml
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""] # "" indicates the core API group
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
---
# This role binding allows "jane" to read pods in the "default" namespace.
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: user1 # Name is case sensitive
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role #this must be Role or ClusterRole
  name: pod-reader # this must match the name of the Role or ClusterRole you wish to bind to
  apiGroup: rbac.authorization.k8s.io
```

**Once created, you may authenticate into the kube-api server using the users credentials**

```bash
curl -v -k https://localhost:6443/api/v1/pods -u "user1:password123"
```

![Diagram](images/image242.png)

### TLS Basics

Basics of what TLS certificates are, why you need them and how you can configure certificates to secure associates or web servers. 

A certificate is used to guarantee trust between two parties during a transaction. For example, when a user tries to access a web server, TLS certificates ensure that the communication between the user and the server is encrypted and the server is who it says it is.  

Let's take a look at a scenario. without secure connectivity. 

If a user were to access his online banking application, the credentials he types in would be sent in a plain text format. The hacker sniffing network traffic could easily retrieve the credentials and use it to hack into the

user's bank account. Well, that's obviously not safe. So you must encrypt the data being transferred using encryption keys. The data is encrypted using a key, which is basically a set of random numbers and alphabets.

You add the random number to your data and you encrypt it into a format that cannot be recognized. The data is then sent to the server. The hackers sniffing the network gets the data, but can't do anything with it. 

However, the same is the case with the server receiving the data, it cannot decrypt the data without the key.  

So a copy of the key must also be sent to the server so that the server can decrypt and read the message, since the key is also sent over the same network. The attacker can sniff that as well and decrypt the data with it.  

This is known as **symmetric encryption.** It is a secure way of encryption, but since it uses the same key to encrypt and decrypt the data and since the key has to be exchanged between the sender and the receiver, there is a risk of a hacker gaining access to the key and decrypting that data. And that's where **asymmetric encryption** comes in. Instead of using a single key to encrypt and decrypt data, asymmetric encryption uses a pair of keys, a private key and a public key. Well, they are private and public keys, but for the sake of this example, we will call it a private key and a public lock. We will get back to that at the end, but for now, think of it as a key and a lock pair. A key which is only with me, so it's private. A lock that anyone can access.  So it's public. The trick here is if you encrypt or lock that data with your lock, you can only open it with the associated key. So your key must always be secure with you and not be shared with anyone else. It's private.  But the lock is public and may be shared with others, but they can only lock  something with it no matter what is locked using the public lock, it can only be unlocked by your private key. 

Before we go back to our Web server example, let's look at an even simpler use case of securing ssh  access to servers using key pairs. You have a server in your environment that you need access to. You don't want to use passwords as they're too risky. So you decide to use key pairs, you generate a public and private key pair.

![Diagram](images/image126.png)

You can do this by running the `ssh-keygen` command. It creates two files. **id_rsa** is the private key and **id_rsa.pub** the public key. “*Well, not a public key a public lock*”. You then secure your server by locking down all access to it, except through a door that is locked using your public lock. It's usually done by adding an entry with your public key into the server’s. `~/.ssk/authorized_keys` file. So you see, the lock is public and anyone can attempt to break through. But as long as no one gets their hands on your private key, which is safe with you on your laptop, no one can gain access to the server. When you try to ssh, you specify the location of your private key in your ssh command.**What if you have other servers in your environment?** 

**How do you secure more than one server with your key pair?** 

Well, you can create copies of your public lock and place them on as many servers as you want. You can use the same private key to ssh into  all of your servers securely. 

**What if other users need access to your servers?**

Well, they can do the same thing. They can generate their own public and private key pairs, as the only person who has access to those servers you can create an additional door for them and lock it with their public locks. 

Copy their public locks to all the servers, and now other users can access the servers using their private keys.

Let's go back to our web server example. You see, the problem we had earlier with symmetric encryption was that the key used to encrypt data had to be sent to the server over the network along with the encrypted data.  And so there is a risk of the hacker getting the key to decrypt the data. **What if we could somehow get the key to the server safely was the keys safely made available to the**

**server?** The server and client can safely continue communication with each other using symmetric encryption.

To securely transfer the symmetric key from the client to the server, we use asymmetric encryption, so we generate a public and private key pair on the server.  “*We're going to refer to the public lock as public key going forward.”* Now that you have got the idea, the `ssh-keygen` command was used earlier to create a pair of keys

![Diagram](images/image352.png)

![Diagram](images/image143.png)

for ssh purposes.  So the format is a bit different. Here we use the `openssl` command to generate a private and public key pair. And that's how they look.

When the user first accesses the Web server using https, he gets the public key from the server,  since the hacker is sniffing all traffic, let us assume he too gets a copy of the public key. We'll see what he can do with it.  

The user, in fact, the user's browser then encrypts the symmetric key using the public key provided by the server. The symmetric key is now secure.  The user then sends this to the server. The hacker also gets a copy.

The server uses the private key to decrypt the message and retrieve the symmetric key from it. However, the hacker does not have the private key to decrypt and retrieve the symmetric key from the message received.

The hacker only has the public key, which he can only lock or encrypt a message and not decrypt the message.

The symmetric key is now safely available only to the user and the server that can now use the symmetric key to encrypt data and send to each other. The receiver can use the same symmetric key to decrypt data and retrieve information. The hacker is left with the encrypted messages and public keys with which he can’t  decrypt any data.

With asymmetric encryption, we have successfully transferred the symmetric keys from the user to the

server and with symmetric encryption We have secured all future communication between them.

The hacker now looks for new ways to hack into your account, and so he realizes that the only way he can get your credential is by getting you to type it into a form he presents. So he creates a website that looks exactly like your bank's website. The design is the same. The graphics are the same. The website is a replica of the actual bank's website. He hosts the website on his own server. He wants you to think it's secure, too, so he generates his own set of public and private key pairs and configures them on his web server. And finally, he somehow manages to tweak your environment or your network to route your requests going to your bank's website to his servers. When you open up your browser and type the website address in, you see a very familiar page, the same login page of your bank that you're used to seeing. So you, you go ahead and type in the username and password. You make sure you type in https in the URL to make sure the communication is secure and encrypted. Your browser receives a key. You send an encrypted symmetric key and then you send your credentials encrypted with the key, and the receiver decrypts the credentials with the same symmetric key. You've been communicating securely in an encrypted manner, but with the hackers server, as soon as you

send in your credentials, you see a dashboard that doesn't look very much like your bank's dashboard. 

What if you could look at the key you received from the server and say if it is a legitimate key from

the real bank server, when the server senses the key, it does not send the key along. It sends a certificate that has the key in it. If you take a closer look at the certificate, you will see that it is like an actual certificate,

but in a digital format, it has information about who the certificate is issued to the public key of that server, the location of that server, etc.. On the right, you'll see the output of an actual certificate, every certificate has a name on it, the person or subject to whom the certificate is issued to that is very important, as that is the field that helps you validate their identity. If this is for a web server, this must match what the user types in the URL on his browser. If the bank is known by any other names and if they like their users to access their application with the other names as well, then all those names should be specified in this certificate under the subject

alternative names section. **But do you see anyone who can generate a certificate like this?**  You could generate one for yourself by saying your Google, and that's what the hacker did. In this case, he generated a certificate saying he is your bank's website. So how do you look at a certificate and verify if it is legit? That is where the most important part of the certificate comes into play. Who signed and issued the certificate? If you generated a certificate, then you will have to sign it by yourself. That is known as a self signed certificate. Anyone looking at the certificate you generated will immediately know that it is not a safe certificate because you have signed it. If you looked at the certificate you received from the hacker closely, you would have noticed that it was a fake certificate that was signed by the hacker himself. As a matter of fact, your browser does that for you. All of the web browsers are built in with a certificate validation mechanism wherein the browser checks the certificate received from the server and validates it to make sure it is legitimate. If it identifies it to be a fake certificate, then it actually warns you. **Then how do you create a legitimate certificate for your web servers that the web browsers will trust? How do you get your certificates signed by someone with authority?**

![Diagram](images/image8.png)

![Diagram](images/image73.png)

That's where certificate authorities or CAs come in. They're well known organizations that can sign and validate your certificates for you. Some of the popular ones are **Symantec**, DigiCert Comodo, Global Sign, etc.The way this works is you generate a certificate signing request or **CSR** using the key you generated earlier and the domain name of your website. You can do this again using the `openssl` command. This generates my-bank.csr  file, which is the certificate signing request that should be sent to the CA for signing. It looks like this.  

The certificate authorities verify your details, and once it checks out, they sign the certificate and send it back to you. You now have a certificate signed by a CA that the browsers trust.  If Hacker tried to get his certificate signed the same way, he would fail during the validation phase and his certificate would be rejected by the CA.

![Diagram](images/image236.png)

So the website that he's hosting won't have a valid certificate.

The CA's use different techniques to make sure that you're the actual owner of that domain. You now have a certificate signed by a CA that the browsers trust.

**But how do the browsers know that the CA itself was legitimate? For example, what if the certificate was signed by a fake CA?** In this case, our certificate was signed by Symantec. How would the browser know Symantec is a valid CA and that the certificate was in fact signed by Symantec and not by someone who

says they are Symantec.  The CAs themselves have a set of public and private key pairs. The CAs use their private keys to sign the certificates. The public keys of all the keys are built into the browsers. The browser uses the public key of the CA to validate that the certificate was actually signed by the CA themselves.

You can actually see them in the settings of your web browser under certificates. They're under the Trusted CAs  tab.  

Now, these are public CAs that help us ensure the public websites we visit, like our banks, emails,

etc. are legitimate. However, they don't help you validate sites hosted privately within your organization.

For example, for accessing your payroll or internal email applications. For that, you can host your own private CAs.  Most of these companies listed here have a private offering of their services and CA server that you can deploy internally within your company. You can then have the public key of your internal CA server installed on all your employees browsers and establish secure connectivity within your organization. 

So let's summarize real quick. We have seen why you may want to encrypt messages being sent over a network. To encrypt messages we use asymmetric encryption with a pair of public and private keys, and admin  uses a pair of keys to secure ssh connectivity to the servers. The server uses a pair of keys to secure HTTPS  traffic. But for this, the server first sends a certificate signing request to a CA. The CA uses its private key to sign the CSR. Remember, all users have a copy of the CAs public key. The signed certificate is then sent back to the server. The server configures the web application with the signed certificate. Whenever a user accesses the web application, the server first sends the certificate with its public key. The user or rather the user's browser, reads the certificate and uses the CAs public key to validate and retrieve the server's public key.

It then generates a symmetric key that it wishes to use going forward for all communication. The symmetric key is encrypted using the server's public key and sent back to the server. The server uses its private key to decrypt the message and retrieve the symmetric key. The symmetric key is used for communication going forward, so the administrator generates a key pair for securing accesses. The web server generates a key pair for securing the website with a step.  Yes. The certificate authority generates its own set of key pairs to sign certificates. The end user, though, only generates a single symmetric key. Once he establishes trust with the website, he uses his username and password to authenticate to the web server. 

But in the service key paris, the client was able to validate that the server is who they say they are, but the server does not for sure know if the client is who they say they are. It could be a hacker impersonating a user by somehow gaining access to his credentials.Not over the network, for sure, as we have secured it already. Tell us, maybe by some other means anyway. So what can the server do to validate that the client is who they say they are for this as part of the initial trust building exercise? The server can request a certificate from the client. And so the client must generate a pair of keys. Have a signed certificate from a valid CA The client then sends the certificate to the server for it to verify that the client is who they say they are. Now you must be thinking you have never generated a client certificate to access a website. Well, that's because TLS client certificates are not generally implemented on web servers. Even if they are, it's all implemented under the hood. So a normal user doesn't have to generate and manage certificates manually. So that was the final piece about client certificates. This whole infrastructure, including the CA, the servers, the people and the process of generating, distributing and maintaining digital certificates is known as public key infrastructure, or PKI. Finally, let me clear up something before you leave. I've been using the analogy of a key and lock for private and public keys. If I give you the impression that only the lock or the public key can encrypt data, then please forgive me as it's not true. These are in fact, two related or paired keys. You can encrypt data with any one of them and only decrypt data with the other. You cannot encrypt data with one and decrypt with the same. So you must be careful what you encrypt your data with. If you encrypted data with your private key, then remember anyone with your public key, which could really be anyone out there will be able to decrypt and read your message.

Finally, a quick note on naming convention usually certificates with public key are named *.crt or *.pem extension. So that's server.crt server.pem for server certificates or client.crt or client.pem for client certificates, and private keys are usually with extension .key or *-key.pem.  For example, server.key or server-key.pem.

 So just remember, private keys have the word key in them   usually either as an extension or in the name of the certificate. And one that doesn't have the word key in them is usually a public key or certificate.

### TLS IN KUBERNETES

Securing your kubernetes cluster with TLS certificates.  In the previous lecture we saw what public and private keys are, how a server uses public and private keys to secure connectivity.  We will call them servering certificates.  We saw what a certificate authority is. We learned that the CA has its own set of public and private keypairs  that it uses to sign server certificates.  We will call them root certificates. We also saw how a server can request a client to verify themselves using client certificates.  

So three types of certificates, 

- server certificates configured on the servers

- root certificate configured on the CA servers and then

- Client certificates configured on the clients.

![Diagram](images/image332.png)

And a quick note on naming convention before we go forward. You're going to see a lot of certificate files in this lecture and it could be very confusing.So use this technique to know which one is which. Usually certificates with **public keys** are named *.crt or *.pem extension. So that's server.crt or server.pem. for server certificates or client.crt or client.pem  for client certificates. And private keys are usually with extension *.key or with a *-key.pem in the filenames, eg : server.key or server-key.pem So just remember, private keys have the word key in them, usually either as an extension or in the name of the certificate and one that doesn't have the word key in them is usually a public key or certificate. That's how to remember it.

![Diagram](images/image407.png)

![Diagram](images/image34.png)

We will now see how these concepts relate to a kubernetes cluster. The kubernetes cluster consists of a set of master and worker nodes, of course, all communication between these nodes need to be secure and must be encrypted. All interactions between all services and their clients need to be secure. For example, an administrator interacting with the kubernetes cluster through the kubectl utility or via accessing the kubernetes API directly must establish secure TLS connection. Communication between all the components within the kubernetes cluster also needs to be secured. So the two primary requirements are to have all the various services within the cluster to use server certificates and all clients to use client certificates to verify they are who they say they are. Let's look at the different components within the kubernetes cluster and identify the various servers and clients and who talks to who.

Let's start with the **KubeAPI** server .As we know already, the API server exposes an https service that other components as well as external users use to manage the kubernetes cluster. So it is a server and it requires certificates to secure all communication with its clients.  So we generate a certificate and keep it here. We call it **apiserver.cert** and **apiserver.key.**  We will try to stick to this naming convention going forward. Anything with a *.crt extension is the certificate and *.key extension is the private key.

Also remember, the certificate names could be different in different kubernetes setups depending on who and how the cluster was set up. So these names may be different in yours. In this lecture, we will try to use names that help us easily identify the certificate files.  Another server in the cluster is the ETCD server, the ETCD, the server stores, all the information about the cluster, so it requires a pair of certificate and key for itself. **We will call it etcdserver.crt and etcdserver.key.**  The other server component in the cluster is on the worker nodes. They are the Kubelet services. They also expose an https API endpoint that the kubeAPI server talks to, to interact with the worker nodes. Again, that requires a certificate and key pair. **We call it kubelet.crt and kubelet.key.**

Those are really the server components in the kubernetes cluster.  

Let's now look at the **client components**, who are the clients who access the services, the clients who access the kubeAPI server  are us **The administrators** to kubectl or REST API. The admin user requires a certificate and keypair to authenticate to the server. **We will call it admin.crt and admin.key.**

The scheduler talks to the API server to look for PODs that require scheduling and then get the kubeAPI server to schedule the PODs on the right worker nodes. The scheduler is a client that accesses the kubeAPI server. As far as the kubeAPI server is concerned, the scheduler is just another client, like the admin user. So the scheduler needs to validate its identity using a client TLS certificate so it needs its own pair of certificate and keys. **We will call it scheduler.crt and scheduler.key.**

The Kube-controller-manager is another client that accesses the kubeAPI server, so it also requires a certificate for authentication to the kubeAPI server.So we create a certificate pair for it.**We will call it kubectl.cert and kubectl.key.**

The last client component is the kube-proxy, the kube-proxy requires a client certificate to authenticate to the API server and so it requires its own pair of certificate and keys. **We will call them kubeproxy.crt and kubeproxy.key.**

![Diagram](images/image391.png)

The servers communicate amongst them as well. For example, the kubeAPI server communicates with the ETCD server. In fact, of all the components, the kubeAPI server is the only server that talks to the etcd server. So as far as the server is the ETCD server is concerned, the kubeAPI server is a client, so it needs to authenticate. The kubeAPI server can use the same keys that it used earlier for serving its own API service. **the apiserver.cert** and **apiserver.key.** Or you can generate a new pair of certificates specifically for the server to authenticate to the etcd server. The kubeAPI server also talks to the kubelet server on each of the individual nodes. That's how it monitors the worker nodes. For this again, it can use the original certificates or generate new ones specifically for this purpose.So that's too many certificates.  Let's try and group them. There are a set of client certificates mostly used by clients to connect to the kubeAPI server, and there are a set of server side certificates used by the server, ETCD server and kubeAPI server to authenticate their clients.

![Diagram](images/image7.png)

We will now see how to generate these certificates. As we know already, we need a certificate authority to sign all of these certificates. kubernetes requires you to have at least one certificate authority for your cluster. In fact, you can have more than one, one for all the components in the cluster and another one specifically for ETCD. In that case, the ETCD servers certificates and the servers client certificates, which in this case is the API server client certificate, will be all signed by the ETCD servers CA/ For now, we will stick to just one seet for our customer.The CA  as we know, has its own pair of certificates and keys. We will call it **CA.crt and CA.key.** That should sum up all the certificates used in the cluster.

### TLS in Kubernetes-Certificate Creation

In this lecture, we'll look at how to generate the certificates for the cluster. To generate certificates there are different tools available such as EasyRSA, OpenSSL or CFSSL, etc. or many others. In this lecture we will use openSSL tool to generate the certificates. This is where we left off. We will start with the CA certificates.

![Diagram](images/image335.png)

![Diagram](images/image144.png)

![Diagram](images/image54.png)

First, we create a private key using the openSSL command `openSSL genrsa -out ca.key`. Then we use the openSSL request command along with the key which is created to generate a certificate signing request.The certificate signing request is like a certificate with all of your details, but with no signature.In the certificate signing request, we specify the name of the component the certificate is for in the common name or CN field. In this case, since we are creating a certificate for the Kubernetes CA, we name it KUBERNETES-CA. Finally, we sign the certificate using the openSSL x509 command and by specifying the certificate signing request we generated in the previous command. Since this is for the CA itself, it is self signed by the CA using its own private key that it generated in the first step. Going forward for all other certificates, we will use this CA key, a key pair to sign them. The CA now has its private key and root certificate file. Let's now look at generating the client certificates. We start with the admin user. We follow the same process where we create a private key for the admin user using the openSSL command. We then generate a CSR and that is where we specify the name of the admin user, which is kube-admin.  A quick note about the name It doesn't really have to be kube-admin it could be anything but remember, this is the name that kube control client authenticates with and when you run the kubectl command, so in the audit logs and elsewhere, this is the name that you will see so provide a relevant name in this field. Finally generate a signed certificate using the open SSL x509 command. But this time you specify the CA certificate and the CA key. You're signing your certificate with the CA key pair  that makes this a valid certificate within your cluster. The signed certificate is then output to admin.crt file. That is the certificate that the admin user will use to authenticate to Kubernetes cluster. If you look at it, this whole process of generating a key and a certificate pair is similar to creating a user account for a new user. The certificate is the validated user ID and the key is like the password. It's just that it's much more secure than a simple username and password. So this is for the admin user. **How do you differentiate this user from any other users?** The user account needs to be identified as an admin user and not just another basic user. You do that by adding the group details for the user in the certificate. In this case, a group named System masters exist on Kubernetes with administrative privileges. We will discuss about groups later, but for now it's important to note that you must mention this information in your certificate signing request. You can do this by adding group details with the OU parameter while generating a certificate signing request. Once it's signed we now have our certificate for the admin user with admin privileges. We follow the same process to generate client certificates for all other components that access the kubeAPI server.The kube scheduler Now the kube-scheduler is a system component part of the Kubernetes control plane, so its name must be prefixed with the keyword system.The same with kube controller manager.It is again a system component, so its name must be prefixed with the keyword system and finally kube-proxy.

So far we have created CA certificates, then all of the client certificates, including the admin user, scheduler, controller, manager and Kube-proxy. We will follow the same procedure to create the remaining three client certificates for API servers in kubelets. When we create the server certificates for them, so we will set them aside for now.

![Diagram](images/image379.png)

![Diagram](images/image422.png)

**Now, what do you do with these certificates?** Take the admin certificate, for instance, to manage the cluster. You can use this certificate instead of a username and password in a rest API call you make to the kubeAPI server. You specify the key, the certificate and the CA certificate as options. That's one simple way. The other way is to move all of these parameters into a configuration file called kube-config. Within that, specify the API server endpoint details, the certificates to use, etc. That is what most of the Kubernetes clients use.We will look at cube config in depth in one of the upcoming lectures.

So we are now left with the server side certificates. But before we proceed, one more thing. Remember in the prerequisite lecture, we mentioned that for clients to validate the certificates sent by the server and vice versa, they all need a copy of the Certificate Authority's public certificate, the one that we said is already installed within the user's browsers in case of a web application. Similarly, in Kubernetes, for these various components to verify each other, they all need a copy of the CA’s root certificate. So whenever you configure a server or a client with certificates, you will need to specify the CA  root certificate as well. Let's look at the server side certificates. Now, let's start with the ETCD server. We follow the same procedure as before to generate a certificate for ETCD We will name it at ETCD-SERVER. ETCD Server can be deployed as a cluster across multiple servers as in a high availability environment. In that case, to secure communication between the different members in the cluster, we must generate additional peer certificates. Once the certificates are generated, specify them while starting the ETCD Server. There are key and cert file options where you specify the ETCD Server keys. There are other options available for specifying the PEER certificates and finally, as we discussed earlier, it requires the CAs root certificate to verify that the clients connecting to the ETCD server are valid.

![Diagram](images/image223.png)

![Diagram](images/image365.png)

![Diagram](images/image331.png)

**Let's talk about the API server now.**We generate a certificate for the API server like before. **But wait,** the API server is the most popular of all components within the cluster. Everyone talks to the kubeAPI server, every operation goes through the kubeAPI server anything moves within the cluster, the API server knows about it. You need information, you talk to the API server and so it goes by many names and aliases within the cluster. Its real name is Kube-API server, but some call it Kubernetes because for a lot of people who don't really know what goes under the hood of Kubernetes, the Kube-API server is Kubernetes. Others like to call it **kubernetes.default**, while some refer to it as **kubernetes.default.svc**, and some like to call it by its full name **Kubernetes.default.svc.cluster.local.** Finally, it is also referred to in some places simply by its **IP address**, the IP address of the host running the Kube-API server or the POD running it. So all of these names must be present in the certificate generated for the kube API server. Only then those referring to the API server by these names will be able to establish a valid connection. So we used the same set of commands as earlier to generate a key in the certificate signing request. You specify the name Kube API server.

![Diagram](images/image118.png)

**But how do you specify all the alternate names for that?** You must create an open SSL config file, create an openSSL.cnf file and specify the alternate names in the [alt_names] section of the file. Include all the DNS names. The API server goes by as well as the IP address pass this config file as an option while generating the certificate signing request. Finally sign the certificate using the CA certificate and key. You then have the Kube API server certificate. 

![Diagram](images/image147.png)

It is time to look at where we are going to specify these keys. Remember to consider the API client certificates that are used by the API server while communicating as a client to the ETCD and Kublet servers.The location of these certificates are passed in to the kubeAPI server's executable or service configuration file. First, the CA file needs to be passed in. Remember, every component needs to CA certificate to verify its clients.  Then we provide the API server certificates under the TLS cert options. We then specify the client certificates used by kubeAPI server to connect to the ETCD Server again with the CA file. And finally the kubeAPI server client certificates to connect to the kubelets.

Next comes the kubelet server. The kubelet server is an HTTPS API server that runs on each node responsible for managing the node. That's who the API server talks to, to monitor the node, as well as send information regarding what PODs to schedule on this node. As such, you need a key certificate pair for each node in the cluster. **Now what do you name these certificates?** Are they all going to be named kubelets? No, They will be named after their nodes Node01, node02 and Node03. Once the certificates are created, use them in the kubelet config file. As always, you specify the root CA  certificate and then provide the kubelet node certificates. You must do this for each node in the cluster.

We also talked about a set of client certificates that will be used by the kubelet to communicate with the kube-API server. These are used by the kubelet to authenticate into the kue-API server, they need to be generated as well. **What do you name these certificates?** The API server needs to know which node is authenticating and give it the right set of permissions. So it requires the nodes to have the right names in the right formats. Since the nodes are system components like the kube scheduler and the controller manager we talked about earlier, the format starts with the **system** keyword followed by node and then the node name in this case Node01 to Node03. **And how would the API server give it the right set of permissions?** Remember, we specified a group name for the admin user, so the admin user gets administrative privileges. Similarly, the nodes must be added to a group named system nodes. Once the certificates are generated, they go into the kube config files, as we discussed earlier. In the next lecture, we will see how you can view certificate information and how certificates are configured by the kubeadm tool.

### Tls In Kubernetes - Certificate Creation

There are different tools available, such as Easy RSA, Open SSL or CFSSL, etc. or many others. In this lecture, we will use openSSL tools to generate the certificates. This is where we left off. We will start with the CA certificates.

First, we create a private key using the open SSL command, open SSL genrsa -out CA.key.`$ openssl genrsa -out ca.key 2048`

Then we use the open SSL request command along with the key, which is created to generate a certificate signing request. `$ openssl req -new -key ca.key -subj "/CN=KUBERNETES-CA" -out ca.csr`

The certificate signing request is like a certificate with all of your details, but with no signature. In the certificate signing request, we specify the name of the component.  This certificate is for the common name or CN field. In this case, since we are creating a certificate for the `KUBERNETES-CA`, we named i`t Kubernetes- CA.`

Finally, we signed the certificate using the open SSL x509 Command and by specifying the certificate signing request we generated in the previous command

```bash
Sign certificates
$ openssl x509 -req -in ca.csr -signkey ca.key -out ca.crt
```

![Diagram](images/image79.png)

Since this is for the CA itself, it is self signed by the CA using its own private key that it generated in the first step.

Going forward for all other certificates we will use to CA keypair to sign them. 

The CA  now has its private key and root certificate file. 

Great ! Let's now look at generating the client certificates.

We start with the admin user. We follow the same process where we create a private key for the admin user using the open SSL command.We then generate a CSR and that is where we specify the name of the admin user, which is kubeadmin.A quick note about the name. It doesn't really have to be kubeadmin it could be anything. But remember, this is the name that kubectl client authenticates with and when you run the kubectl Command. So in the audit logs and elsewhere, this is the name that you will see. So provide a relevant name in this field.

```bash
$ openssl genrsa -out admin.key 2048$ openssl req -new -key admin.key -subj "/CN=kube-admin" -out admin.csr
```

Finally, generate a signed certificate using the open SSL Ex-fighter nine command.

But this time you specify the CA certificate and the CA key here signing a certificate with the CA keypair that makes this invalid certificate within your cluster. 

```bash
$ openssl x509 -req -in admin.csr -CA ca.crt -CAkey ca.key -out admin.crt
```

![Diagram](images/image312.png)

The signed certificate is then output to the admin.crt file. That is the certificate that the admin user will use to authenticate to Kubernetes cluster.

If you look at it, this whole process of generating a key and a certificate pair is similar to creating a user account for a new user.

The certificate is the validated user ID and the key is like the password. It's just that it's much more secure than a simple username and password. 

So this is for the admin user. **How do you differentiate this user from any other users?**

The user account needs to be identified as an admin user and not just another basic user.  You do that by adding the group details for the user in the certificate.  In this case, a group named System Monsters Inc system Kubernetes with administrative privileges. 

We will discuss about groups later, but for now, it's important to note that you must mention this information in your certificate signing request. You can do this by adding group details with the **O**  parameter while generating certificate signing request.`$ openssl req -new -key admin.key -subj "/CN=kube-admin/O=system:masters" -out admin.csr`

Once it's signed, we now have our certificate for the admin user with admin privileges.

We follow the same process to generate client certificates for all other components that access the KubeAPI Server

The Kube Scheduler Now the scheduler is a system component part of the Kubernetes control plane, so its name must be prefixed with the keyword system.

The same with Kube Controller Manager. It is again a system component, so its name must be prefixed with the keyword system. And finally, kube proxy. So far we have created CA certificates, then all of the client certificates, including the admin user, scheduler, controller, manager and proxy.We will follow the same procedure to create the remaining three client certificates for API servers and kubelets when we create the server certificates for them, so we will set them aside for now.

**Now what do you do with these certificates?** Take the admin certificate, for instance, to manage the cluster. You can use this certificate instead of a username and password in the rest API call you make to the kubeAPI server.

You specify the key, the certificate and the CA certificate as options. That's one simple way.The other way is to move all of these parameters into a configuration file called kube config. Within that, specify the API server endpoint details, the certificates to use, etc. That is what most of the corporate entities clients use.

We will look at kube config in-depth in one of the upcoming lectures. OK, so we are now left with the server side certificates, but before we proceed.One more thing . Remember, in the prerequisite lecture, we mentioned that for clients to validate the certificates sent by the server and vice versa, they all need a copy of the Certificate Authority's public certificate, the one that we said is already installed within the user's browsers in case of a web application. 

Similarly, in Kubernetes, for these various components to verify each other, they all need a copy of the CA root certificate. So whenever you configure a server or a client with certificates, you will need to specify the CA root certificate as well.

Let's look at the server side certificates now. Let's start with the ETCD server. 

We follow the same procedure as before to generate a certificate for ETCD 

We will name it at ETCD-server.

*ETCD can be deployed as a cluster across multiple servers as in high availability environment, in that case to secure communication between the different members in the cluster. We must generate additional peer certificates once the certificates are generated. Specify them while starting the ETCD server.*

![Diagram](images/image361.png)

There are key and cert file options where you specify the ETCD server keys.There are other options available for specifying the peer certificates. 

And finally, as we discussed earlier, it requires to CA root certificate to verify that the clients connecting to the ETCD server are valid.

Let's talk about the API server now.

*We generate a certificate for the API server like before, but wait API server is the most popular of all components within the cluster. Everyone talks to the kube API server. Every operation goes through the kube API server. Anything moves within the cluster, The API server knows about it. You need information, you talk to the API server, and so it goes by many names and aliases within the cluster.*

Its real name is kube API server, but some call it Kubernetes, because for a lot of people who don't really know what goes under the hood of Kubernetes, the kube API server is Kubernetes. Others like to call it Kubernetes stop default. 

while, some refer to it as Kubernetes.default.svc, and some like to call it by its full name. `Kubernetes.default.svc.cluster.local.` Finally, it is also referred to in some places simply by its IP address. The IP address of the host running the kube API server or the POD running it. So all of these names must be present in the certificate generated for the kube API server. Only then those referring to the kubeAPI server by these names will be able to establish a valid connection.So we used the same set of commands as earlier to generate a key in the certificate signing request, you specify the name kubeAPI server. But how do you specify all the alternate names for that, you must create an open **SSL config file,** create an openssl.cnf file and specify the alternate names in the alt names section of the file include all the DNS names the API server goes by, as well as the IP address pass this config file as an option while generating the certificate signing request, finally sign the certificate using the CA Certificate and key.

![Diagram](images/image91.png)

You then have the kube API server certificate. It is time to look at where we are going to specify these keys. 

![Diagram](images/image412.png)

Remember to consider the API client certificates that are used by the API server while communicating as a client to the ETCD  end kubelet servers.

The location of these certificates are passed in to the kubeAPI server’s, executable or service configuration file.First, the CA file needs to be passed in, remember every component Needs a CA certificate to verify its clients.Then we provide the API server certificates under the TLS cert  options. We then specify the client certificates used by kubeAPI Server to connect to the ETCD server. Again, with the CA file. And finally, the kubeAPI server client certificates to connect to the kubelets.

Next comes the kubelet server. The kubelet server is an https  API server that runs on each node responsible for managing the node.That's where the API server talks to to monitor the node, as well as any information regarding what PODs to schedule on this node.As such, you need a key certificate pair for each node in the cluster. 

Now what do you name these certificates?Are they all going to be named kubelets?

![Diagram](images/image103.png)

No, they will be named after their nodes node01, node02 and node03

Once the certificates are created. Use them in the Kublet config file.  As always, you specify the root CA certificate and then provide the kube node certificates. You must do this for each node in the cluster. We also talked about a set of client certificates that will be used by the kubelet to communicate with the kube API server. These are used by the kubelet  to authenticate into the kube API server. They need to be generated as well.  **What do you name these certificates?** 

![Diagram](images/image44.png)

The API server needs to know which node is authenticated and give it the right set of permissions, so it requires the nodes to have the right names in the right format. Since the nodes are system components like the scheduler and the controller manager we talked about earlier, the format starts with the system keyword followed by node and then the node name. 

- In this case, node01 to node03 and how would the API  server give it the right set of permissions?

- Remember, we specify a group name for the admin user, so the admin user gets administrative privileges.

- Similarly, the nodes must be added to a group named system nodes once the certificates are generated.

- They're going to the kube config files, as we discussed earlier.

### VIEW CERTIFICATE DETAILS

**How we can view certificates in an existing cluster?**So you join a new team to help them manage their kubernetes environment. You are a new administrator to this team and you are being told that there are multiple issues related to certificates in the environment so you are asked to perform a health check of all the certificates in the entire cluster. **What do you do ?** first of all It's important to know how the cluster was set up. There are different solutions available for deploying a kubernetes cluster and they use different methods to generate and manage certificates. If you were to deploy a kubernetes cluster from scratch you generate all the certificates by yourself as we did in the previous lecture or else if you were to rely on an automated provisioning tool like kubeadm, it takes care of automatically generating and configuring the cluster for you while you deploy all the components as native services on the nodes in the hard way, the kubeadm tool deploys these as PODs. 

![Diagram](images/image347.png)

So it's important to know where to look at, to view the right information.  In this lecture we are going to look at a cluster provisioned by kubeadm as an example.  In order to perform a health check. Start by identifying all the certificates used in the system. I have created a sample Excel spreadsheet for you. Check out the resources link at the end of this lecture to access it.  So the idea is to create a list of certificate files used. their pods with the names configured on them. The alternate names configured if any, the organisation, the certificate account belongs to. The issue of the certificate and the expiration date on the certificate. **So how do you get these ?**Start with the certificate files used. For this, in an environment setup by kube-adm look for the kubeAPI server definition file under /etc/kubernetes/manifests folder.

![Diagram](images/image342.png)

The command used to start the api server has information about all the certificates it uses. Identify the certificate file used for each purpose and note it down. Next take each certificate and look inside it to find more details about that certificate.For example, we will start with the apiserver certificate file. Run the openssl x509 command  and provide the certificate file as input to decode the certificate and view details.`$ openssl x509 -in /etc/kubernetes/pki/apiserver.crt -text -noout`

![Diagram](images/image112.png)

![Diagram](images/image319.png)

Start with a name on the certificate under the subject section.In this case it's `CN= kube-apiserver.` Then the alternative names. The kube-api server has many, so you must ensure all of them are there and then check the validity section of the certificate to identify the expiry date and then the issuer of the certificate. This should be the CA who issued the certificate. Kubeadm names the kubernetes CA as kubernetes itself. Follow the same procedure to identify information about all the other certificates things to look for,  check to make sure you have the right names, the right alternate names make sure the certificates are part of the correct organization and most importantly you are issued by the right issuer and that the certificates are not expired. 

The certificate requirements are listed in detail in the Kubernetes Documentation page. Check the references section for the link. When you run into issues you want to start looking at logs if you set up the cluster from scratch by yourself and the services are configured as native services in the OS you want to start looking at the service logs using the operating systems logging functionality. `$ journalctl -u etcd.service -l`

![Diagram](images/image278.png)

In case you setup the cluster with kubeadm, then the various components are deployed as PODs. So you can look   at the logs using kubectl logs command followed by the pod name. Sometimes if the core components

![Diagram](images/image260.png)

`$ kubectl logs etcd-master`

such as the kubernetes api server or the etcd server are down, the kubectl commands wont function. In that case  you have to go one level down to docker to fetch the logs. List all the containers using the docker ps –a command. And then view the logs using docker logs command followed by the container ID.

```bash
$ docker ps -a
$ docker logs <container-id>
```

![Diagram](images/image153.png)

#### Certificate Health Check Spreadsheet

[https://github.com/mmumshad/kubernetes-the-hard-way/tree/master/tools](https://github.com/mmumshad/kubernetes-the-hard-way/tree/master/tools) -- Certificate Health Check Spreadsheet

![Diagram](images/image362.png)

### CERTIFICATES API

We look at how to manage certificates and what the certificate API is in kubernetes. So what have we done so far? I as an administrator of the cluster in the process of setting up the whole cluster have set up a CA server and a bunch of certificates for various components. We then started the services using the right certificates and it's all up and working. And as the only administrator and user of the cluster, I have my own admin certificate and key, when a new admin comes into my team. She needs access to the cluster.  We need to get her a pair of certificate and a key pair for her to access the cluster. She creates her own private key, generates a certificate signing request and sends it to me since I'm the only admin. I then take the certificate signing request to my CA server, get it signed by the CA using the CA server's private key and root certificate, thereby generating a certificate and then send the certificate back to her.

She now has her own valid pair of certificate and key that she can use to access the cluster, the certificates have a validated period and it ends after a period of time. Every time it expires we follow the same process of generating a new CSR and getting it signed by the CA. So we keep rotating the certificate files. So we keep talking about the CA server. 

**What is the CA server and where is it located in the Kubernetes setup?** The CA It is really just a pair of key and certificate files we have generated. Whoever gains access to these pair of files, can sign any certificate for the kubernetes environment. They can create as many users as they want, and whatever privileges they want. So these files need to be protected and stored in a safe environment. Say we place them on a server that is fully secure. Now that server becomes your CA server. The certificate key file is safely stored in that server and only on that server every time you want to sign a certificate you can only do it by logging into that server. As of now we have the certificates placed on the kubernetes master node itself. So the master node is also our CA server. The kubeadm tool does the same thing. It creates a CA pair of files and stores that on the master node itself. So far we have been signing requests manually but as and when the users increase and your team grows you need a better automated way to manage the certificates signing requests as well as to rotate certificates when they expire. 

Kubernetes has a built-in **Certificates API** that can do this for you. With the Certificates API, you now send a CertificateSigningRequest directly to kubernetes through an API call. This time, when the administrator receives a certificate signing request instead of logging onto the master node and signing the certificate by himself, he creates a Kubernetes API object called CertificateSigningRequest.

![Diagram](images/image63.png)

Once the object is created all certificates signing requests can be seen by administrators of the cluster. The request can be reviewed and approved easily using kubectl commands; this certificate can then be extracted and shared with the user. Let’s see how it is done. A user first creates a key. Then generates a certificate signing request using the key with her name in it.

```bash
$ openssl genrsa -out jane.key 2048$ openssl req -new -key jane.key -subj "/CN=jane" -out jane.csr 
```

Then sends the request to the administrator. The administrator takes the key and creates a `CertificateSigningRequest` object. ----`apiVersion: certificates.k8s.io/v1beta1`

```yaml
kind: CertificateSigningRequest
metadata:
  name: jane
spec:
  groups:
  - system:authenticated
  usages:
  - digital signature
  - key encipherment
  - server auth
  request:
    <certificate-goes-here>
$ cat jane.csr |base64 $ kubectl create -f jane.yaml 
```

![Diagram](images/image166.png)

The `CertificateSigningRequest` object is created like any other kubernetes object using a manifest file with the usual fields. The kind is `CerificateSingingRequest`. Under the spec section, specify the groups the user should be part of and list the usages of the account as a list of strings. The request field is where you specify the certificate signing request sent by the user but you don't specify it as plain text instead it must be encoded using the base64 command then move the encoded text into the request field and then submit the request once the object is created all certificate signing requests can be seen by administrators by running the kubectl get csr command. Identify the new request and approve the request by running the kubectl certificate approve command. Kubernetes signs the certificate using the CA key pairs and generates a certificate for the user.

This certificate can then be extracted and shared with the user view the certificate by viewing it in a YAML format. The generate certificate is part of the output. But as before it is in a base64 encoded format to decode it. Take the text and use the base 64 utilities decode option. This gives the certificate in a plain text format. 

This can then be shared with the end user. Now that we have seen how it works let's see who does all of this for us. 

If you look at the kubernetes control plane, you see the kube-api server, the scheduler, controller manager, etcd server etc. Which of these components is actually responsible for all the certificate related operations all the certificate related operations are carried out by the controller manager. If you look closely at the controller or manager you will see that it has controllers in it called as csr-approving, csr-signing etc that are responsible for carrying out these specific tasks.  

To list the csr's `$ kubectl get csr`

Approve the request `$ kubectl certificate approve jane`

To view the certificate `$ kubectl get csr jane -o yaml`

To decode it `$ echo "<certificate>" |base64 --decode`

![Diagram](images/image324.png)

![Diagram](images/image295.png)

![Diagram](images/image306.png)

We know that if anyone has to sign certificates, they need the CA servers root certificate and private key. The controller manager service configuration has two options where you can specify these. 

### KubeConfig

So far we have seen how to generate a certificate for a user. We have seen how a client uses the certificate file and key to query the kubernetes Rest API for a list of pods using Curl. 

In this case my cluster is called my-kube-playground, so send a CURL request to the address of the kube-api server while passing in the pair of files along with the ca certificate as options. 

![Diagram](images/image254.png)

![Diagram](images/image109.png)

This is then validated by the API server to authenticate the user.**Now how do you do that while using the kubectl command?** You can specify the same information using the options --server, **--client-key, --client-certificate** and **--certificate-authority** with the kubectl utility. Obviously typing those in every time is a tedious task. So you move this information to a configuration file called as **KubeConfig**. And then specify this file as the --kubeconfig option in your command. By default the kubectl tool looks for a file named config under a directory .kube, under the user's home directory(`$HOME/.kube/config`). So if you create the KubeConfig file there, you don’t have to specify the path to the file explicitly in the kubectl command. That’s the reason you haven’t been specifying any options for your kubectl commands so far. The kubeconfig file is in a specific format. Let’s take a look at that. 

The config file has 3 sections. 

- Clusters,

- Users and

- Contexts.

**Clusters** are the various kubernetes clusters that you need access to. So you have multiple clusters for development environment or testing environment or prod or for different organizations or on different cloud providers etc. All those go there  

**Users** are the user accounts  with which you have access to these clusters. For example the **admin user**, A **Dev User**, a **prod user** etc. These users may have different privileges on different clusters. Finally **contexts** marry these together. Context defines which user account will be used to access which cluster. For example you could create a context named admin at production that will use the admin account to access a production cluster. Or I may want to access the cluster I have set up on Google with the dev users credentials to test deploying the application I built. Remember you're not creating any new users or configuring any kind of user access or authorization in the cluster with this process. You're using existing users with their existing privileges and defining what user you're going to use to access what cluster.  That way you don’t have to specify the user certificates and server address in each and every kubectl command you run. 

**So how does it fit into our example?** The server specification in our command goes into the cluster section, the admin users keys and certificates goes into the users section. You then create a context that specifies to use the MyKubeAdmin user to access the MyKubePlayground cluster. Let’s look at a real KubeConfig file now. The kubeConfig is in a YAML format. 

![Diagram](images/image178.png)

It has apiVersion set to v1. The kind is config. And then it has 3 sections as we discussed. One for clusters, one for contexts and one for users. Each of these is in an array format. That way you can specify multiple clusters, users or contexts within the same file. Under clusters we add a new item for our kube-playground cluster. We name it mukubeplayground and specify the server address under the server field.

It also requires the certificate of the Certificate Authority. We then add an entry into the users section to specify details of my kube admin user. Provide the location of the client’s certificate and key pair. So we have now defined the cluster and the user to access the cluster. 

Next we create an entry under the context section to link the two together we will name the context.my kube admin at my kube playground. We will then specify the same name we used for a cluster and user follow the same procedure to add all the clusters you daily access the user credentials you use to access them as well as the context. Once the file is ready remember that you don’t have to create any object like you usually do for other kubernetes objects. The file is left as is and is read by the kubectl command and the required values are used. 

**Now, how does kubectl know which context to chose from?** We have defined three contexts here which one should it start with. You can specify the default context to use by adding a field **current-context** to the kubeconfig file. specify the name of the context you use. In this case kubectl will always use the context dev-user@google to access the google clusters using the dev-user’s credentials.

There are command line options available within kubectl to view and modify the kubeconfig files.  

To view the current file being used. run the kubectl config view command. It lists the clusters, contexts and users as well as the current-context set.  

To view the current file being used

```bash
$ kubectl config view
```

As we discussed earlier, if you do not specify which kubeconfig file to use, it ends up using the default file located in the folder .kube in users home directory.

Alternatively you can specify a kubeconfig file by passing the kubeconfig option in the command line like this.

*You can specify the kubeconfig file with kubectl config view with "--kubeconfig" flag*

```bash
$ kubectl config veiw --kubeconfig=my-custom-config
```

![Diagram](images/image47.png)

We will move our custom config to the home directory so this becomes our default config file. **So how do you update your current context?** Say you have been using my-kube-admin user to access my-kube-playground. How do you change the context to use prod-user to access the production cluster? *How do you update your current context? Or change the current context*

```bash
$ kubectl config view --kubeconfig=my-custom-configRun the kubectl  config use-context command to change the current-context to the prod-user@production context.
```

![Diagram](images/image190.png)

This can be seen in the current context field in the file. So yes the changes made by kubectl config command actually reflects in the file.

You can make other changes in the file update or delete items in it using other variations of the kubectl config command. 

Check them out when you get time

![Diagram](images/image105.png)

**What about name spaces ?**

![Diagram](images/image406.png)

 for example Each cluster may be configured with multiple name spaces within it. **Can you configure a context to switch to a particular namespace. ?**Yes! The context section in the kubeconfig file can take additional field called namespace where you can specify a particular namespace. This way when you switch to that context you will automatically be in a specific namespace. Finally a word on certificates.You have seen path to certificate files mentioned in kubeconfig like this.

![Diagram](images/image116.png)

Well, its better to use the full path like this. 

![Diagram](images/image13.png)

![Diagram](images/image348.png)

But remember there is also another way to specify the certificate credentials. Let’s look at the first one for instance where we configure the path to the Certificate Authority.We have the contents of the ca.crt file on the right. Instead of using the certificate-authority field and the path to the file. you may optionally use the certificate-authority-data field and provide the contents of the certificate itself. 

But not the file as is, Convert the contents to a base64 encoded format and then pass that in. Similarly if you see a file with the certificates data in the encoded format use the Base64 decode option to decode the certificate.

### API Groups

Before we head into authorization it is necessary to understand about API groups in kubernetes.

![Diagram](images/image334.png)

But first, **what is the Kubernetes API?**We learned about the Kube API server. Whatever operations we have done so far with the cluster, we have been interacting with the API server one way or the other. Either through the kubectl utility or directly via REST. Say we want to check the version, we can access the api server at the master nodes address followed by the port which is 6443 by default and the API version. It returns the version. Similarly to get the list of pods, you would access the url api/v1/pods.Our focus in this lecture is about these API paths. The /version and /api. The Kubernetes API is grouped into multiple such groups based on their purpose. Such as one for apis, one for healthz, metricsand logs etc. The version API is for viewing the version of the cluster as we just saw The Matrix and healthz api are used to monitor the health of the cluster. The logs for integrating with third party logging applications. In this lesson we will focus on the API that is responsible for the cluster of functionality, These APIs are categorized into two. The core group and the named group.

![Diagram](images/image353.png)

The core group is where all core functionality exists. Such as namespaces, pods, replication controllers, events, endpoints, nodes, bindings, Persistent volumes, persistent volume claims, configmaps, secrets, services etc. 

![Diagram](images/image250.png)

The named group API is are more organised and going forward all the newer features are going to be made available to these named groups. 

![Diagram](images/image423.png)

It has groups under it for apps, extensions, networking, storage, authentication, authorization certificates etc. Shown here are just a few. Within apps, you have deployments, replicasets, statefulsets. Within networking you have network policies. Certificates have these certificates sign requests that we talked about earlier in the section so the ones at the top are API groups and the ones at the bottom are resources in those groups.

Each resource in this has a set of actions associated with them. Things that you can do with these resources such as list the deployments get information about one of these deployments create a deployment delete a deployment update a deployment watch a deployment etc. These are known as verbs. 

The Kubernetes API reference page can tell you what the API group is for each object select an object and the first section in the documentation page shows its group details .

![Diagram](images/image180.png)

v1/core is just v1. 

You can also view these on your Kubernetes cluster. Access your kube-api server at port 6443, without any path and it will list you the available api groups. And then within the named api groups it returns all supported groups.

![Diagram](images/image175.png)

 **A quick note on accessing the cluster API like that.** 

If you were to access the API directly through curl as shown here, then you will not be allowed access except for certain APIs like version, as you have not specified any authentication mechanisms. So you have to authenticate to the API using your certificate files by passing them in the command line like this. 

![Diagram](images/image329.png)

 An alternate option is to start a kubectl proxy client.The kubectl proxy command launches a proxy service locally on port 8001 and uses credentials and certificates from your kubeconfig file to access the cluster.

![Diagram](images/image4.png)

That way you don’t have to specify those in the curl command. Now you can access the kubectl proxy service at port 8001 and the proxy will use the credentials from kube-config file to forward your request to the kube api server. This will list all available APIs at root. so here are 2 terms that kind of sound the same.The **Kube proxy** and **kubectl proxy** well they are not the same. We discussed about kube-proxy earlier in this course. It is used to enable connectivity between PODs and services across different nodes in the cluster.  We discuss about kube-proxy in much more detail later in this course.Whereas kubectl proxy is an HTTP proxy service created by kubectl utility to access the kube-api server.

![Diagram](images/image78.png)

So what to take away from this. All resources in Kubernetes are grouped into different api groups. At the top level you have core api group and named api group. 

Under the named api group You have one for each section under this API group.You have the different resources and each resource has a set of associated actions known as verbs In the next section on authorization. We can see how we use these to allow or deny access to users.

### Authorization

So far, we talked about authentication. We saw how someone can gain access to a cluster.We saw different ways that someone, a human or a machine can get access to the cluster. Once they gain access. **What can they do?** That's what authorization defines.

**First of all, why do you need authorization in your cluster as an administrator of the cluster?**We were able to perform all sorts of operations in it, such as viewing various objects like ports and nodes and deployments, creating or deleting objects such as adding or deleting PODs, or even nodes in the cluster. As an admin We're able to perform any operation.  

But soon we will have others accessing the cluster as well, such as the other administrators, developers, testers or other applications like monitoring applications or continuous delivery applications like Jenkins, et cetera. 

![Diagram](images/image164.png)

So we will be creating accounts for them to access the cluster by creating usernames and passwords or tokens or signed certificates or service accounts, as we saw in the previous lectures. 

But we don't want all of them to have the same level of access as us. For example, We don't want the developers to have access to modify our cluster configuration, like adding or deleting nodes or the storage or networking configurations.  We can allow them to view, but not modify. But they could have access to deploying applications.The same goes with service accounts. We only want to provide the external application, the minimum level of access to perform its required operations. When we share our cluster between different organizations or teams by logically partitioning it using namespaces, we want to restrict access to the users to their name spaces alone. 

**That is what authorization can help you within the cluster.** There are different authorization mechanisms supported by Kubernetes, such as 

- node authorization,

- attribute based authorization,

- rule based authorization and

- webhook.

Let us  go through these now.

![Diagram](images/image267.png)

We know that the kubeapi server is accessed by users like us for management purposes, as well as the kubelets  on nodes within the cluster for management purposes within the cluster. The Kubelet accesses the API server to read information about services and points, nodes and PODs.The Kubelet also reports to the kubeAPI server, with information about the note such as its status.

These requests are handled by a special authorizer known as the **node authorizer**. In the earlier lectures when we discussed about certificates. We discussed that the kubelets should be part of the system nodes group and have a name prefixed with system node. So any requests coming from a user with the name system node and part of these system nodes group is authorized by the node authorizer and are granted these privileges. the privileges required for a kubelet so that's access within the cluster.

Let's talk about external access to the API, for instance, a user **attribute based authorisation** is where you associate a user or a group of users with a set of permissions.  In this case, we say the dev user can view, create and delete PODs. You do this by creating a policy file with a set of policies defined in a JSON format. This way. 

![Diagram](images/image259.png)

 You pass this file into the API server.  Similarly, we create a policy definition file for each user or group in this file.

Now, every time you need to add or make a change in the security, you must edit this policy file manually and restart the Kube API server as such.  The attribute based access control configurations are difficult to manage.

We will look at **role based access contro**l next.

**Role based access controls** make these much easier. With role based access controls instead of directly associating a user or a group with a set of permissions. We define your role, in this case for developers. We create a role with the set of permissions required for developers. Then we associate all the developers to that role. 

![Diagram](images/image281.png)

Similarly, create a role for security users with the right set of permissions required for them. Then associate the user to that role. Going forward whenever a change needs to be made to the users access, we simply modify the role and it reflects on all developers immediately.

Role based access control to provide a more standard approach to managing access within the Kubernetes cluster.

We will look at role based access controls in much more detail in the next lecture. 

For now, let's proceed with the other authorization mechanisms. 

**Now, what if you want to outsource all the authorization mechanisms?** 

Say you want to manage authorization externally and not through the built in mechanisms that we just discussed?

![Diagram](images/image222.png)

For instance, **open policy agent** is a third party tool that helps with admission control and authorization. 

You can have Kubernetes, make an API call to the **open policy agent** with the information about the user and his access requirements and have the open policy agent decide if the user should be permitted or not. Based on that response, the user is granted access. 

Now, there are two more modes, in addition to what we just saw. 

![Diagram](images/image234.png)

**Always allow** and **always denied** as the name states always allow, allows all requests without performing any authorization checks. 

Always deny, denies, all requests. 

**So where do you configure these modes?**

**Which of them are active by default?**

**Can you have more than one at a time?**

**How does authorization work if you do have multiple ones configured?** 

The modes are set using the authorization mode option on the kubeAPI server, if you don't specify this option, it is set to always allow by default, you may provide a comma separated list of multiple modes that you wish to use. 

In this case, I want to set it to Node RBAK and webhook. When you have multiple modes configured.

![Diagram](images/image402.png)

Your request is authorized using each one in the order it is specified.

For example, when a user sends a request, it's first handled by the note authorizer.

The note authorizer handles only no requests. So it denies the request whenever a module denies the request, it is forwarded to the next one in the chain.

The role based access control module performs its checks and grants. The user permission, authorization is complete and user is given access to the requested object. So every time a module denies a request, it goes to the next one in the chain. And as soon as a module approves the request, no more checks are done and the user is granted permission.

![Diagram](images/image58.png)

### Role Based Access Controls

In this lecture, we look at **role-based access controls** in much more detail.

**So how do we create a role?**We do that by creating a role object. So we create a role definition file with the API version set to rbac.authorization.k8s.io/v1 and kind set to Role.  We name the role developer as we are creating this role for developers and then we specify rules.

Each rule has three sections- 

- apiGroups,

- resources, and

- verbs.

The same things that we talked about in one of the previous lectures. For the core group You can leave the API group's section blank and  for any other group you specify the group name and the resources that we want to give developers access to are pods.   The actions that they can take are **list**, **get**, **create** and **delete**. To allow the developers to create configmaps,we add another rule to create ConfigMap.  

We can add multiple rules for a single role like this. 

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer
rules:
- apiGroups: [""] # "" indicates the core API group
  resources: ["pods"]
  verbs: ["get", "list", "update", "delete", "create"]
- apiGroups: [""]
  resources: ["ConfigMap"]
  verbs: ["create"]
```

Create the role using the kubectl create role command. 

```bash
$ kubectl create -f developer-role.yaml
```

The next step is to link the user to that role. For this we create another object called RoleBinding. The role  binding object links a user object to a role. 

We will name it devuser-developer-binding. The kind is RoleBinding. `apiVersion: rbac.authorization.k8s.io/v1` `kind: RoleBinding``metadata:`  `name: devuser-developer-binding``subjects:``- kind: User`  `name: dev-user # "name" is case sensitive`  `apiGroup: rbac.authorization.k8s.io``roleRef:`  `kind: Role`  `name: developer`  `apiGroup: rbac.authorization.k8s.io`

*It has two sections. The subjects is where we specify the user details. The roleRef section is where we provide the details* of the role we created. Create the role binding using the kubectl create command.

```bash
$ kubectl create -f devuser-developer-binding.yaml
```

![Diagram](images/image369.png)

Also note that the roles and role bindings fall under the scope of **namespace**.  

So here the dev-user gets access to pods and configmaps within the default namespace. If you want to limit the dev user's access within a different namespace then specify the namespace within the metadata of the definition file while creating them to view the created roles. Run the kubectl get roles command to list role bindings. Run the kubectl get rolebindings command to view more details about the role, run the kubectl describe role developer command. 

```bash
To list roles
$ kubectl get roles
To list rolebindings
$ kubectl get rolebindings
To describe role and rolebinding
$ kubectl describe role developer
```

Here you see the details about the resources and permissions for each resource. 

Similarly To view details about role bindings run the kubectl  describe role bindings command. 

```bash
$ kubectl describe rolebinding devuser-developer-binding
```

Here you can see details about an existing role binding.

**What if you being a user would like to see if you have access to a particular resource in the cluster ?** 

You can use the kubetl auth can -i command and check if you can, say create deployments. Or say delete nodes. 

```bash
$ kubectl auth can-i create deployments
$ kubectl auth can-i delete nodes
```

If you are an administrator then you can even impersonate another user to check their permission.

  For instance say you are tasked to create necessary set of permissions for a user to perform a set of operations and you did that but you would like to test if what you did is working.

You don't have to authenticate as the user to test it. Instead you can use the same command with the as user option like this

```bash
$ kubectl auth can-i create deployments --as dev-user
$ kubectl auth can-i create pods --as dev-user
```

 since we did not grant the developer permissions to create deployments it returns no.

 The dev user has access to creating pods though. You can also specify the namespace in the command like this.

```bash
$ kubectl auth can-i create pods --as dev-user --namespace test
```

The dev-user does not have permission to create a pod in the test namespace.

![Diagram](images/image381.png)

Well a quick note on resource names we just saw how you can provide access to users for resources like pods within the namespace.

You can go one level down and allow access to specific resources alone. 

For example, say you have five pods in the namespace. You want to give access to a user to pods, but not all pods. You can restrict access to the blue and orange pod alone by adding a resourceNames field to the rule.

![Diagram](images/image205.png)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer
rules:
- apiGroups: [""] # "" indicates the core API group
  resources: ["pods"]
  verbs: ["get", "update", "create"]
  resourceNames: ["blue", "orange"]
```

### CLUSTER ROLES

We discussed roles and role bindings in the previous lecture. 

In this lecture we will talk about cluster roles and cluster role bindings

When we talked about roles and role bindings, We said that roles and role bindings are namespaced, meaning they are created within namespaces. If you don't specify in the namespace they're created in the default namespace and control access within that namespace alone. In one of the previous lectures we discussed about name spaces and how it helps in grouping or isolating resources like pods, deployments and services. 

![Diagram](images/image339.png)

**But what about other resources like nodes? Can you group or isolate nodes within a namespace? Like can you say node01 is part of the dev namespace ?**

No, those are cluster wide or cluster scoped resources. They cannot be associated to any particular namespace. So the resources are categorized as either namespaced or cluster scoped. 

![Diagram](images/image302.png)

Now we have seen a lot of namespaced resources throughout this course. Like pods, replicasets, and jobs, deployments, services, secrets, and in the last lecture we saw two new, Roles and Rolebindings.

![Diagram](images/image245.png)

These resources are created in the namespace you specify when you create them. If you don't specify a namespace they are created in the default namespace.To view them or delete them or update them you always specify the right namespace. 

The cluster scoped resources are those where you don’t specify a namespace when you create them. Like nodes, persistent volumes, persistent clusterroles and clusterrolebinding, that we're going to look at In this lecture

Certificate signing requests we saw earlier and namespace objects themselves are of course not namespaced.

Note that this is not a comprehensive list of resources to see a full list of namespace and non namespace resources run the kubectl api-resources command with the namespaced option set.

```bash
$ kubectl api-resources --namespaced=true
```

To see non-namespaced resources

```bash
$ kubectl api-resources --namespaced=false
```

 In the previous lecture we saw how to authorize a user to namespace resources. We used Roles and Rolebindings for that. But how do we authorize users to cluster wide resources like nodes or persistent volumes that is where you use cluster roles and cluster role bindings. Cluster roles are just like roles except they are for a cluster scoped resource for example a cluster admin role can be created to provide a cluster administrator permissions to view, create or delete nodes in a cluster. 

Similarly if storage administrator role can be created to authorize a storage admin to create persistent volumes and claims create a cluster all definition file with the kind cluster roll and specify the rules as we did before this case.

![Diagram](images/image393.png)

The resources are nodes then create the cluster role.The next step is to link the user to that cluster role.

For this we create another object called cluster role binding.The role binding object links the user to the role.

Cluster Roles are roles except they are for a cluster scoped resource. Kind as **ClusterRole**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-administrator
rules:
- apiGroups: [""] # "" indicates the core API group
  resources: ["nodes"]
  verbs: ["get", "list", "delete", "create"]

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cluster-admin-role-binding
subjects:
- kind: User
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-administrator
  apiGroup: rbac.authorization.k8s.io
```

We will name it **cluster-admin-role-binding**. The kind is **ClusterRoleBinding**. Under subjects we specify the user details, cluster-admin-user in this case the **roleRef** section is where we provide the details of the cluster role we created and create the role binding using the kubectl create command one thing to note. 

```bash
$ kubectl create -f cluster-admin-role.yaml
$ kubectl create -f cluster-admin-role-binding.yaml
```

![Diagram](images/image336.png)

Before I let you go we said that cluster roles and bindings are used for clusters of resources but that is not a hard rule you can create a cluster role for namespace resources as well. 

When you do that the user will have access to these resources across all name spaces. Earlier when we created a role to authorize a user to access pods the user had access to the pods in a particular namespace alone.

With cluster rules when you authorize a user to access the pods the user gets access to all pods across the cluster. Kubernetes creates a number of cluster roles by default, when the cluster is first setup. 

practice question michelle's responsibilities are growing and now she will be responsible for storage as well. Create the required ClusterRoles and ClusterRoleBindings to allow her access to Storage.

Get the API groups and resource names from command kubectl api-resources. Use the given spec:

- ClusterRole: storage-admin

- Resource: persistentvolumes

- Resource: storageclasses

- ClusterRoleBinding: michelle-storage-admin

- ClusterRoleBinding Subject: michelle

- ClusterRoleBinding Role: storage-admin

Solution ---

```yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: storage-admin
rules:
- apiGroups: [""]
  resources: ["persistentvolumes"]
  verbs: ["get", "watch", "list", "create", "delete"]
- apiGroups: ["storage.k8s.io"]
  resources: ["storageclasses"]
  verbs: ["get", "watch", "list", "create", "delete"]

---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: michelle-storage-admin
subjects:
- kind: User
  name: michelle
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: storage-admin
  apiGroup: rbac.authorization.k8s.io
```

### SERVICE ACCOUNTS

In this lecture, we will talk about service accounts in Kubernetes. The concept of service accounts is linked to other security related concepts in Kubernetes, such as authentication,authorization, role based access controls, etc.. 

However, as part of the Kubernetes for the application developers exam curriculum, you only need to know how to work with service accounts. We have detailed sections covering the other concepts and security in the Kubernetes administrators course.

So there are two types of accounts in Kubernetes, 

- a user account and

- a service account,

As you might already know, the user account is used by humans and service accounts are used by machines. A user account could be for an **administrator** accessing the cluster to perform administrative tasks or a **developer** accessing the cluster to deploy applications, etc..

A service account could be an account used by an application to interact with a Kubernetes cluster, for example, a monitoring application like Prometheus uses a service account to pull the Kubernetes API for performance metrics and an automated build tool like Jenkins uses service accounts to deploy applications on the Kubernetes cluster.

![Diagram](images/image72.png)

Let's take an example.

![Diagram](images/image123.png)

 I've built a simple Kubernetes dashboard application named my_kubernetes_dashboard.  It's a simple application built in Python, and all that it does when deployed is retrieve the list of PODs on a Kubernetes cluster by sending a request to the Kubernetes API and displaying it on a web page. 

In order for my application to query the Kubernetes API, it has to be authenticated. For that, we use a service account.To create a service account Run the command kubectl create service account, followed by the account name, which is dashboard-sa  

```bash
$ kubectl create serviceaccount dashboard-saThat said, in this case. To view the service accounts, run the kubectl get service account command. This will list all the service accounts.
$ kubectl get serviceaccount
```

When the service account is created, it also creates a token automatically, the service account token is what must be used by the external application while authenticating to the Kubernetes API. 

The token, however, is stored as a secret object. In this case, it's named `dashboard-sa-token-kbbdm`.

![Diagram](images/image167.png)

So when a service account is created, it first creates the service account object and then generates a token for the service account.

It then creates a secret object and stores that token inside the secret object. 

The secret object is then linked to the service account to view the token, view the secret object by running the command `$ kubectl describe secret dashboard-sa-token-kbbdm`

![Diagram](images/image417.png)

This token can then be used as an authentication bearer token while making a REST call to the Kubernetes API, for example, in this simple example, using CURL, you could provide the bearer token as an authorization header while making errors call to the Kubernetes API in case of my custom dashboard application.Copy and paste the token into the tokens field to authenticate the dashboard application.

![Diagram](images/image388.png)

`curl` [https://192.168.56.70:6443/api](https://192.168.56.70:6443/api) `-insecure --header “Autherization: bearer eyJhbG…”` 

So that's how you create a new service account and use it.

You can create a service account, assign the right permissions using role based access control mechanisms, which is out of scope for this course, and export your service account tokens and use it to configure your third party application to authenticate to the Kubernetes API. 

**But what if your third party application is hosted on the Kubernetes cluster itself?**

For example, we can have our custom Kubernetes dashboard application or the Prometheus application deployed on the Kubernetes cluster itself.  

In that case, this whole process of exporting the service account token and configuring the third party application to use it can be made simple by automatically mounting the service token secret as a volume inside the POD, hosting the third party application.

That way, the token to access the Kubernetes API is already placed inside the POD and can be easily read by the application. You don't have to provide it manually. 

If you go back and look at the list of service accounts, you will see that there is a default service account that exists already. For every namespace kubernetes, a service account named **default** is automatically created.

Each namespace has its own default service account.Whenever a POD is created. The default service account and its token are automatically mounted to that POD as a volume mount.

For example, we have a simple port definition file that creates a pod using my custom Kubernetes dashboard image.

We haven't specified any secrets or volume mounts  in the definition file.However, when the port is created, if you look at the details of the pod by running the kubectl describe pod command, you see that a volume is automatically created from the secret named default token, which is in fact the secret containing the token for the default service account.  

The secret token is mounted at location `/var/run/secrets/kubernetes.io/serviceaccount` inside the pod.

![Diagram](images/image208.png)

So from inside the pod, if you run the ls Command to list the contents of the directory, you will see the Secret mounted as three separate files. 

![Diagram](images/image411.png)

- The one with the actual token is the file named token.  If you view contents of that file, you will see the token to be used for accessing the Kubernetes API.

Now, remember that the default service account is very much restricted. It only has permission to run basic common API queries. If you'd like to use a different service account, such as the one we just created, modify the pod definition file to include a service account field and specify the name of the new service account.

Remember, you cannot edit the service account of an existing pod. You must delete and recreate the pod.

However, in case of a deployment, you will be able to edit the service account as any changes to the pod definition file will automatically trigger a new rollout for the deployment. 

So the deployment will take care of deleting and recreating new pods with the right service account.

When you look at the pod details now, you see that the new service account is being used. 

![Diagram](images/image316.png)

You may choose not to mount a service account automatically by setting the Auto Mount Service Account token field to false in the pod’s spec section.

```yaml
controlplane ~ ✖ cat /var/rbac/dashboard-sa-role-binding.yaml
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: dashboard-sa # Name is case sensitive
  namespace: default
roleRef:
  kind: Role #this must be Role or ClusterRole
  name: pod-reader # this must match the name of the Role or ClusterRole you wish to bind to
  apiGroup: rbac.authorization.k8s.io
```

Enter the access token in the UI of the dashboard application. Click Load Dashboard button to load Dashboard

Retrieve the Authorization token for the newly created service account , copy it and paste it into the token field of the UI.

To do this, run kubectl describe against the secret created for the dashboard-sa service account, copy the token and paste it in the UI.

Task 

You shouldn't have to copy and paste the token each time. The Dashboard application is programmed to read token from the secret mount location. However currently, the 'default' service account is mounted. Update the deployment to use the newly created ServiceAccount

Edit the deployment to change ServiceAccount from 'default' to 'dashboard-sa'

- Deployment name: web-dashboard

- Service Account: dashboard-sa

- Deployment Ready

solution: 

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-dashboard
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      name: web-dashboard
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      creationTimestamp: null
      labels:
        name: web-dashboard
    spec:
      serviceAccountName: dashboard-sa
      containers:
      - image: gcr.io/kodekloud/customimage/my-kubernetes-dashboard
        imagePullPolicy: Always
        name: web-dashboard
        ports:
        - containerPort: 8080
```

          `protocol: TCP`   

### IMAGE SECURITY

We will start with the basics of image names and then work our way towards secure image repositories and how to configure your PODs to use images from secure repositories.  We deployed a number of different kinds of PODs hosting different kinds of applications throughout this course, like web apps and databases and redis cash, et cetera. 

Let's start with a simple, POD definition file, for instance. 

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
  - name: nginx
    image: nginx
```

Here we have used the nginx image to deploy an nginx container. Let's take a closer look at this image name. The name is nginx, but what is this image and where is this image pulled from? This name follows Dockers image naming convention and nginx here is the image or the repository name.  

When you say nginx, it's actually library slash nginx.

![Diagram](images/image249.png)

 The first part stands for the user or the account name, so if you don't provide a user or account name, it assumes it to be a library.  Library is the name of the default account where Docker's official images are stored. These images promote best practices and are maintained by a dedicated team who are responsible for reviewing and publishing these official images.  Now, if you were to create your own account and create your own repositories or images under it, then you would use a similar pattern instead of a library. It would be your name or your company's name. 

**Now, where are these images stored and pulled from?** Since we have not specified the location where these images are to be pulled from, it is assumed to be Dockers default registry.Docker Hub, the DNS name for which is **docker.io**. The registry is where all the images are stored.  

![Diagram](images/image127.png)

Whenever you create a new image or update an image, you push it to the registry, and every time anyone deploys this application, it is pulled from the registry.

There are many other popular registries as well. Google's registry is at GCR.io where a lot of Kubernetes related images are stored, like the ones used for performing end to end tests on the cluster.

These are all publicly accessible images that anyone can download and access when you have applications built in-house that shouldn't be made available to the public.  Posting an internal private registry may be a good solution.Many cloud service providers, such as AWS, Azure or GCP, provide a private registry by default.On any of these solutions be it on Docker Hub or Google's registry or your internal private registry.

You may choose to make a repository private so that it can be accessed using a set of credentials. 

From doctor’s perspective, to run a container using a private image, you first log in to your privateregistry using their doctor, log in command,

```bash
$ docker login private-registry.io
```

input your credentials. On successful run the application using the image from the private registry. 

Going back to our POD definition file to use an image from our private registry, we replaced the image name with the full path to the one in the private registry.

**But how do we implement the authentication log in part?** 

**How does kubernetes get the credentials to access the private registry?**

```bash
$ docker run private-registry.io/apps/internal-app
```

Within kubernetes, we know that the images are pulled and run by the docker runtime on the worker node.

![Diagram](images/image146.png)

```bash
$ docker run private-registry.io/apps/internal-app
```

**How do you pass the credentials to the docker run time, on the worker nodes ?**

For that, we first create a secret object with the credentials in it. 

The secret is of type Docker registry and we name it, RegCredit Docker registry is a built in secret type that was built for storing Docker credentials.We then specified the registry server name the username to access the registry, the password and the email address of the user. We then specify the secret inside our poor definition file under the image pull secret section when the plot is created, Kubernetes or the Kubernetes on the worker node uses the credentials from the secret to pull images.

*To pass the credentials to the docker untaged on the worker node for that we first create a secret object with credentials in it.*

```bash
$ kubectl create secret docker-registry regcred \
  --docker-server=private-registry.io \ 
  --docker-username=registry-user \
  --docker-password=registry-password \
  --docker-email=registry-user@org.com
```

*We then specify the secret inside our pod definition file under the imagePullSecret section*`apiVersion: v1`

```yaml
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
  - name: nginx
    image: private-registry.io/apps/internal-app
  imagePullSecrets:
  - name: regcred
```

![Diagram](images/image18.png)

### Pre-requisite – Security in Docker

### Security Contexts

Security Contexts in Kubernetes.As we saw in the previous lecture when you run a docker container you have the option to define a set of security standards such as the ID of the user used to run the container, The Linux capabilities that can be added or removed from the container etc. These can be configured in Kubernetes as well. As you know already, in Kubernetes containers are encapsulated in PODs. You may choose to configure the security settings at a container level or at a pod level. If you configure it at a pod level the settings will carry over to all the containers within the pod. If you configure it at both the pod and the container the settings on the container will override the settings on the pod let us start with a pod definition file. 

![Diagram](images/image12.png)

![Diagram](images/image107.png)

This pod runs an ubuntu image with the sleep command. To configure security context on the container, add a field called security context under the specs section of the pod use the to run as a user option to set the userID for the pod.To set the same configuration on the container level move the whole section under the container specification like this to add capabilities use the capabilities optionand specify a list of capabilities to add to the pod.

### Network Policies

![Diagram](images/image385.png)

Network policies. So let us first get our networking and security basics right. Before we begin we will start with a simple example of a traffic flowing through a web app and database server so you have a web server serving front-end to users, an app server serving back-end API and a database server. The user sent in a request to the web server at port 80 the web server then sent a request to the API server at port 5000 in the back end. The API server then fetches data from the database server at Port 3306 and then sends the data back to the user a very simple setup So there are two types of traffic here: ingress and egress. For example for a web server the incoming traffic from the users is an ingress traffic and the outgoing request to the app server is a egress traffic and that is denoted by the straight arrow. When you define ingress and egress remember you're only looking at the direction in which the traffic originated. The response back to the user denoted by the dotted lines do not really matter. Similarly in case of the back end API server it receives ingress traffic from the web server on port 5000 and has egress traffic to port 3306 to the database server, and from the database servers perspective it receives ingress traffic on 3306 from the API server. If we were to list the rules required to get this working we would have an ingress rule that is required to accept HTTP traffic on port 80 on the web server. An Egress rule to allow traffic from the web server to port 5000 on the API server. An ingress rule to accept traffic on port 5000 on the API server and an egress rule to allow traffic to port 3306 on the database server.  And finally an ingress rule on the database server to accept traffic on port 3306. So that's the basic of traffic flow and rules. 

![Diagram](images/image110.png)

Let us now look at Network Security in Kubernetes.So we have a cluster with a set of nodes hosting a set of pods and services. Each node has an IP address and so does each pod as well as service. One of the pre-requisite for networking in kubernetes, is whatever solution you implement, the pods should be able to communicate with each other without having to configure any additional settings like routes. For example, in this network solution, all pods are on a virtual private network that spans across the nodes in the kubernetes cluster. And they can all by default reach each other using the IPs or pod names or services configured for that purpose. Kubernetes is configured by default with an “All Allow” rule that allows traffic from any pod to any other pod or services. Let us now bring back our earlier discussion and see how it fits into kubernetes. For each component in the application we deploy a POD. One for the front-end web server, for the API server and one for the database.  We create services to enable communication between the PODs as well as to the end user. Based on what we discussed in the previous slide, by default all the three PODs can communicate with each other within the kubernetes cluster. What if we do not want the front-end web server to be able to communicate with the database server directly say for example your security teams and audits require you to prevent that from happening. That is where you would implement a Network Policy to allow traffic to the db server only from the api server. 

![Diagram](images/image386.png)

![Diagram](images/image80.png)

![Diagram](images/image152.png)

A Network policy is another object in the kubernetes namespace.Just like PODs, ReplicaSets or Services.You link a network policy to one or more pods.You can define rules within the network policy.In this case I would say, only allow Ingress Traffic from the API Pod on Port 3306. Once this policy is created, it blocks all other traffic to the Pod and only allows traffic that matches the specified rule. Again, this is only applicable to the Pod on which the network policy is applied. So how do you apply or link a network policy to a pod.We use the same technique that was used before to link ReplicaSets or Services to Pods. Labels and Selectors We label the Pod and use the same labels on the pod selector field in the network policy. And then we build our rule under policy types specify whether the rule is to allow ingress or egress traffic or both.In our case we only want to allow ingress traffic to the db-pod. So we add Ingress.Next, we specify the ingress rule, that allows traffic from the API pod. And you specify the api pod, again using labels and selectors.And finally the port to allow traffic on, which is 3306.Let us put all that together.We start with a blank object definition file and as usual we have apiVersion, kind,metadata and spec. The apiVersion is networking.k8s.io/v1,the kind is NetworkPolicy. We will name the policy db-policy. And then under the spec section,we will first move the pod selector to apply this policy to the db pod. Then we will move the rulewe created in the previous slide under it and that's it.We have our first network policy ready. Run the kubectl create command to create the policy. *Remember that Network Policies are enforced by the Network Solution implemented on the Kubernetes Cluster. And not all network solutions support network policies. A few of them that are supported are kube-router, Calico, Romana and Weave-net.* If you used Flannel as the networking solution, it does not support network policies as of this recording. Always refer to the network solution’s documentation to see support for network policies.Also remember even in a cluster configured with a solution that does not support network policies you can still create the policies but they will just not be enforced.You will not get an error message saying the network solution does not support network policies. Walk through the documentation  

### Developing network policies

Network policies in more detail. So here we have the same Web API and database pods that we discussed in the previous lecture. So first, let's be very clear with our requirements. Our goal is to protect the database POD so that it does not allow access from any other pod except the API pod and only on port 3306. So let's assume that we are not concerned about the web pod or the API pod for those pods. We are okay for all traffic to go in and out from anywhere. However, we want to protect the database pod and only allow traffic from the API pod.

So let's get the other things out of our way so we can focus exactly on the required tasks. So we don't need to worry about the web pod or its port, as we don't want to allow any traffic from any other sources other than the API pod. So let's get rid of that. We can also forget about the port on the API pod to which the web server connects as we don't care about that either. As we discussed, by default, Kubernetes allows all traffic from all paths to all destinations. So as the first step, we want to block out everything going in and out of the database pod. So we create a network policy. We will call it **DB policy**.

And the first step is to associate this network policy with the port that we want to protect, and we

do that using labels and selectors.

So we do that by adding a pod selector field with the match labels option and by specifying the label

on the DB pod, which happens to be set to roll db.

And that associates the network policy with the database pod and blocks out all traffic.

However, we need the API pod to be able to query the database on Port 3306.

So that's what we are going to configure next.

First, we need to figure out what type of policies should be defined on this network policy object

to meet our requirements.

So there are two types of policies that we discussed in the previous lecture.

We have ingress and egress.

So do we need ingress or egress here or both?

So you always look at this from the DB pods perspective, from the DB pods perspective.

We want to allow incoming traffic from the API pod.

So that is incoming.

So that is ingress.

The API pod makes database queries and the database pods returns the results.

So what about the results?

Do you need a separate rule for the results to go back to the API pod?

No, because once you allow incoming traffic, the response or reply to that traffic is allowed back

automatically.

We don't need a separate rule for that.

So in this case, all we need is an increased rule to allow traffic from the API pod to the database

pod, and that would allow the API pod to connect to the database and run queries and also retrieve

the result of the queries.

So when deciding on what type of rule is to be created, you only need to be concerned about the direction

in which the request or reach needs, which is denoted by the straight line here.

And you don't need to worry about the response which is denoted by the dotted line.

However, this rule does not mean that the database pod will be able to connect to the API pod or make

calls to the API.

See.

For example, the database pod tries to make an API call to the API pod.

Then that would not be allowed because that is now an egress traffic originating from the database pod

and would require a specific egress rule to be defined.

So I hope you get the difference between the two and are clearer about ingress and egress rules.

I just wanted to make sure that you're clear on what type of policy is to be selected for the requirement

that you have in hand.

So a single network policy can have an ingress type of rule and egress type of rule or both.

In cases where a port wants to allow incoming connections as well as wants to make external calls.

So for now, our use case only requires ingress policy types.

Now that we have decided on the type of policy, the next step is to define the specifics of that policy.

If it's ingress, we create a section called Ingress within which we can specify multiple rules.

Each rule has a from and ports fields.

The from field defines the source of traffic that is allowed to pass through to the database pod.

And here we would use a pod selector and provide the labels of the APA pod like this.

The ports field defines what port on the database port is the traffic allowed to go to?

In this case, it's 3306 with the TCP protocol, and that's it.

This would create a policy that would block all traffic to the DB port except for traffic from the API

pod.

Now what if there are multiple API parts in the cluster with the same labels but in different namespaces?

So say here we have different namespaces for dev test and prod environments and we have the API pod

with the same labels in each of these environments.

The current policy would allow any pod in any namespace with matching labels to reach the database pod.

We only want to allow the API pod in the prod namespace to reach the database pod.

So how do we do that?

For this, we add a new selector called as the namespace selector property along with the pod selector

property.

Under this we use match labels again to provide a label set on the namespace.

And you must remember that you must have this label set on the namespace first for this to work.

So that's what the namespace selector does.

It helps in defining from what namespace traffic is allowed to reach the database pod.

Now what if you only have the namespace selector and not the pod selector like this?

In this case, all pods within the specified namespace will be allowed to reach the database pod, such

as the web pod that we had earlier.

But pods from outside this namespace won't be allowed to go through.

Let's look at another use case.

Say we have a backup server somewhere outside of the Kubernetes cluster, and we want to allow this

server to connect to the database pod.

Now, since this backup server is not deployed in our Kubernetes cluster, the port selector and namespace

selector fields that we use to define traffic from won't work because it's not a pod in the cluster.

However, we know the IP address of the backup server and that happens to be one.

92.1.

68 .5. ten.

We could configure a network policy to allow traffic originating from certain IP addresses.

For this, we add a new type of from definition known as the IP block definition.

IP block allows you to specify a range of IP addresses from which you could allow traffic to hit the

database pod.

So those are three supported selectors under the from section and Ingress and these are also applicable

to the two section in ingress and we'll see that in a few minutes.

We have pod selector to select pods by labels.

We have namespace selector to select namespaces by labels and we have the IP block selector to select

IP address ranges.

These can be passed in separately as individual roles or together as part of a single rule.

In this example, under the from section, we have two elements.

So these are two rules.

The first rule has the pod selector and the namespace selector together, and the second rule has the

IP block selector.

So this works like an all operation traffic from sources meeting.

Either of these criterias are allowed to pass through.

However, within the first rule we have two selectors.

Part of it that would mean traffic from sources and must meet both of these criteria to pass through.

So they have to be originating from pods with matching labels of API pod and those pods must be in the

pod namespace so it works like an and operation.

Now what if we were to separate them by adding a dash before the namespace selector like this?

Now they are two separate rules.

So this would mean that traffic matching the first rule is allowed, that is from any pod matching the

label API pod in any namespace and traffic matching.

The second rule is allowed, which is from any pod within the pod namespace that is either from the

pod web and of course along with the backup server as we have the IP block specification as well.

So now we have three separate rules and almost traffic from anywhere is allowed to the DB pod.

So a small change like that can have a big impact.

So it's important to understand how you could put together these rules based on your requirements.

So now let's get rid of all of that and go back to a basic set of rules and we'll now look at egress.

So say, for example, instead of the backup server initiating a backup, say we have an agent on the

DB part that pushes back up to the backup server.

In that case, the traffic is originating from the database part to an external backup server.

For this, we need to have egress rule defined.

So we first add egress to the policy types, and then we add a new egress section to define the specifics

of the policy.

So instead of from, we now have to under egress.

So that's the only difference.

Under two, we could use any of the selectors such as a pod namespace or an IP block selector.

And in this case, since the database server is external, we use IP block selector and provide the

CIDR block for the server.

The port to which the requests are to be sent to is 80.

So we specify 80 as the port.

So this rule allows traffic originating from the database bot to an external backup server at the specified

address.

Well, that's it for now.

About network policies and rules.

### Kubectx and Kubens – Command line Utilities

Through out the course, you have had to work on several different namespaces in the practice lab environments. In some labs, you also had to switch between several contexts. 

While this is excellent for hands-on practice, in a real “live” kubernetes cluster implemented for production, there could be a possibility of often switching between a large number of namespaces and clusters. 

This can quickly become and confusing and overwhelming task if you had to rely on kubectl alone. 

This is where command line tools such as kubectx and kubens come in to picture. 

Reference: [https://github.com/ahmetb/kubectx](https://github.com/ahmetb/kubectx)

 **Kubectx:**

With this tool, you don’t have to make use of lengthy “kubectl config” commands to switch between contexts. This tool is particularly useful to switch context between clusters in a multi-cluster environment. 

**Installation:**

```text
sudo git clone https://github.com/ahmetb/kubectx /opt/kubectx
sudo ln -s /opt/kubectx/kubectx /usr/local/bin/kubectx
```

**Syntax:**

To list all contexts:

`kubectx` 

To switch to a new context:

```text
kubectx <context_name>
```

 To switch back to previous context:

```text
kubectx –
```

 To see current context:

```text
kubectx -c
```

**Kubens:**

This tool allows users to switch between namespaces quickly with a simple command.

**Installation:**

```text
sudo git clone https://github.com/ahmetb/kubectx /opt/kubectx
sudo ln -s /opt/kubectx/kubens /usr/local/bin/kubens
```

**Syntax:**

To switch to a new namespace:

```text
kubens <new_namespace>
```

To switch back to previous namespace:

```text
kubens –
```

---

### Modern Projected ServiceAccount Tokens (TokenRequest API)

Starting in Kubernetes 1.24+, ServiceAccount tokens are no longer automatically stored in unbounded, non-expiring Secrets. Instead, Kubernetes uses the **`TokenRequest` API** and **Projected Volumes**.

#### Key Differences (Legacy vs Modern)
- **Legacy (< v1.24):** Long-lived Secret created automatically when a ServiceAccount was created. Token had no expiration and cluster-wide validity.
- **Modern (v1.24+):** Tokens are short-lived (default 1 hour), audience-bound, and dynamically rotated and injected via a projected volume mounted at `/var/run/secrets/kubernetes.io/serviceaccount`.

#### Imperative Token Generation
You can generate short-lived tokens on the fly using `kubectl create token`:
```bash
# Request a token for serviceaccount 'dashboard-sa' with a 2-hour duration
kubectl create token dashboard-sa --duration=2h

# Generate a token with a custom audience (e.g. for HashiCorp Vault or cloud IAM federation)
kubectl create token dashboard-sa --audience=https://vault.internal --duration=30m
```

#### Manually Creating a Permanent ServiceAccount Secret (When Needed)
If a legacy CI/CD system or external tool requires a static, non-expiring Secret token:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: dashboard-sa-token
  namespace: default
  annotations:
    kubernetes.io/service-account.name: "dashboard-sa"
type: kubernetes.io/service-account-token
```
Applying this Secret prompts the Kubernetes token controller to populate the `token` and `ca.crt` fields into the Secret data.

#### Projected Volume Syntax in Pods
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  containers:
  - name: app
    image: alpine
    command: ["sleep", "3600"]
    volumeMounts:
    - mountPath: /var/run/secrets/tokens
      name: vault-token
  volumes:
  - name: vault-token
    projected:
      sources:
      - serviceAccountToken:
          path: vault-token
          expirationSeconds: 7200
          audience: https://vault.internal
```

---

### Admission Controllers

An Admission Controller intercepts requests to the Kubernetes API server **after** the request is authenticated and authorized, but **before** the object is persisted into ETCD.

#### Admission Controller Phases
1. **Mutating Admission:** Can modify/patch the requested object (e.g., inject sidecars, assign default StorageClasses).
2. **Object Schema Validation:** Verifies structural schema conformity.
3. **Validating Admission:** Accepts or rejects the request based on custom policies (e.g., disallowing privileged containers, enforcing label rules).

#### Common Built-in Admission Plugins
- **`NodeRestriction`**: Limits the Node and Pod objects a kubelet can modify (only its own node and pods on it).
- **`AlwaysPullImages`**: Mutates every pod to set `imagePullPolicy: Always`.
- **`LimitRanger`**: Enforces default/min/max compute resource constraints defined by LimitRange objects.
- **`ResourceQuota`**: Enforces namespace resource quotas, rejecting creates if quotas are exceeded.
- **`NamespaceLifecycle`**: Prevents creating resources in non-existent or terminating namespaces, and prevents deleting default system namespaces (`default`, `kube-system`, `kube-public`).

#### Viewing and Configuring Admission Controllers
Admission plugins are configured on the `kube-apiserver` static pod manifest (`/etc/kubernetes/manifests/kube-apiserver.yaml`):

```yaml
# In /etc/kubernetes/manifests/kube-apiserver.yaml
spec:
  containers:
  - command:
    - kube-apiserver
    - --enable-admission-plugins=NodeRestriction,LimitRanger,ResourceQuota,AlwaysPullImages
    - --disable-admission-plugins=DefaultStorageClass
```

#### Helpful Admission Controller Commands
```bash
# Check default enabled admission plugins
kube-apiserver -h | grep enable-admission-plugins

# Query running apiserver pod arguments
kubectl get pod -n kube-system kube-apiserver-controlplane -o jsonpath='{.spec.containers[0].command}' | tr -s ' ' '\n' | grep admission
```

---

### Pod Security Standards (PSS) & Admission (PSA)

Starting in Kubernetes 1.25+ (replacing the deprecated `PodSecurityPolicy`), Kubernetes provides built-in **Pod Security Admission (PSA)** based on three standardized **Pod Security Standards (PSS)** levels:

1. **`Privileged`**: Completely open and unrestricted. Allows running as root, host namespaces (`hostNetwork`, `hostPID`), privileged mode, and arbitrary capabilities.
2. **`Baseline`**: Minimally restrictive policy that blocks known privilege escalations (forbidding `privileged: true`, `hostPID`, `hostNetwork`), but permits running as root.
3. **`Restricted`**: Heavily hardened cloud-native best practice. Mandates rootless execution (`runAsNonRoot: true`), drops all default capabilities except `NET_BIND_SERVICE`, forbids privilege escalation, and enforces read-only root filesystems.

#### Configuring PSA via Namespace Labels

PSA is configured declaratively using namespace labels across three modes:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production-secure
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

#### Modes:
- **`enforce`**: Rejects non-compliant pods during admission with an HTTP 403 error.
- **`audit`**: Permits non-compliant pods but logs an event in the audit log for compliance tracking.
- **`warn`**: Emits a visible warning in the operator's terminal upon `kubectl apply` without rejecting the workload.
