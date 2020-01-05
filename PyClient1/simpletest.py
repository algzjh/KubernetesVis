from kubernetes import client, config, watch
from kubernetes.client import configuration
from kubernetes.client.apis import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from pprint import pprint
import yaml
from os import path
from pick import pick
import time


def init():
    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config(config_file="kubeconfig.yaml")
    global v1
    v1 = client.CoreV1Api()


def listAllPodandIp():
    # 列出所有的 pod 和它们的 IP
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


def listAllNamespace():
    # 列出所有的名称空间
    print("\nListing All namespace:")
    for ns in v1.list_namespace().items:
        print(ns.metadata.name)


def listAllServicesandInfo():
    """
    :return:
    None 	default 	hello-kubernetes 	10.101.187.108 	[{'name': None,
    'node_port': 31618,
    'port': 80,
    'protocol': 'TCP',
    'target_port': 8080}]
    """
    # 列出所有的 service 和它们的信息
    print("\nListing All services with their info:")
    ret = v1.list_service_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s \t%s \t%s \t%s \t%s \n" % (
        i.kind, i.metadata.namespace, i.metadata.name, i.spec.cluster_ip, i.spec.ports))


def testGlobal():
    print(v1)


def createDeploymentFromFile(filename):
    """
    :param filename: "hello-kubernetes.yaml"
    :return:

    """
    with open(path.join(path.dirname(__file__), filename)) as f:
        dep = yaml.safe_load(f)
        resp = v1.create_namespaced_deployment(
            body=dep, namespace="default")
        print("Deployment created. status='%s'" % resp.metadata.name)


def discoveryApi():
    """
    :return:
    Supported APIs (* is preferred version):
    core                                     v1
    apiregistration.k8s.io                   *v1,v1beta1
    extensions                               v1beta1
    apps                                     v1
    events.k8s.io                            v1beta1
    authentication.k8s.io                    *v1,v1beta1
    authorization.k8s.io                     *v1,v1beta1
    autoscaling                              *v1,v2beta1,v2beta2
    batch                                    *v1,v1beta1
    certificates.k8s.io                      v1beta1
    networking.k8s.io                        *v1,v1beta1
    policy                                   v1beta1
    rbac.authorization.k8s.io                *v1,v1beta1
    storage.k8s.io                           *v1,v1beta1
    admissionregistration.k8s.io             *v1,v1beta1
    apiextensions.k8s.io                     *v1,v1beta1
    scheduling.k8s.io                        *v1,v1beta1
    coordination.k8s.io                      *v1,v1beta1
    node.k8s.io                              v1beta1
    """
    print("Supported APIs (* is preferred version):")
    print("%-40s %s" %
          ("core", ",".join(client.CoreApi().get_api_versions().versions)))
    for api in client.ApisApi().get_api_versions().groups:
        versions = []
        for v in api.versions:
            name = ""
            if v.version == api.preferred_version.version and len(
                    api.versions) > 1:
                name += "*"
            name += v.version
            versions.append(name)
        print("%-40s %s" % (api.name, ",".join(versions)))


def customObject():
    """
    Uses a Custom Resource Definition (CRD) to create a custom object, in this case
    a CronTab. This example use an example CRD from this tutorial:
    https://kubernetes.io/docs/tasks/access-kubernetes-api/custom-resources/custom-resource-definitions/
    The following yaml manifest has to be applied first:
    apiVersion: apiextensions.k8s.io/v1
    kind: CustomResourceDefinition
    metadata:
      name: crontabs.stable.example.com
    spec:
      group: stable.example.com
      versions:
        - name: v1
          served: true
          storage: true
      scope: Namespaced
      names:
        plural: crontabs
        singular: crontab
        kind: CronTab
        shortNames:
        - ct
    :return:
    """
    api = client.CustomObjectsApi()

    # it's my custom resource defined as Dict
    my_resource = {
        "apiVersion": "stable.example.com/v1",
        "kind": "CronTab",
        "metadata": {"name": "my-new-cron-object"},
        "cronSpec": "* * * * */5",
        "image": "my-awesome-cron-image",
    }

    # create the resource
    api.create_namespaced_custom_object(
        group="stable.example.com",
        version="v1",
        namespace="default",
        plural="crontabs",
        body=my_resource,
    )
    print("Resource created")

    # get the resource and print out data
    resource = api.get_namespaced_custom_object(
        group="stable.example.com",
        version="v1",
        name="my-new-cron-object",
        namespace="default",
        plural="crontabs",
    )
    print("Resource details:")
    pprint(resource)

    # delete it
    api.delete_namespaced_custom_object(
        group="stable.example.com",
        version="v1",
        name="my-new-cron-object",
        namespace="default",
        plural="crontabs",
        body=client.V1DeleteOptions(),
    )
    print("Resource deleted")


def createUpdateDeleteDeployment():
    # https://github.com/kubernetes-client/python/blob/master/examples/deployment_crud.py
    pass


def createUpdateDeleteJob():
    # https://github.com/kubernetes-client/python/blob/master/examples/job_crud.py
    pass


def listPodsInContext():
    contexts, active_context = config.list_kube_config_contexts()
    if not contexts:
        print("Cannot find any context in kube-config file.")
        return
    contexts = [context['name'] for context in contexts]
    active_index = contexts.index(active_context['name'])
    cluster1, first_index = pick(contexts, title="Pick the first context",
                                 default_index=active_index)
    cluster2, _ = pick(contexts, title="Pick the second context",
                       default_index=first_index)

    client1 = client.CoreV1Api(
        api_client=config.new_client_from_config(context=cluster1))
    client2 = client.CoreV1Api(
        api_client=config.new_client_from_config(context=cluster2))

    print("\nList of pods on %s:" % cluster1)
    for i in client1.list_pod_for_all_namespaces().items:
        print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    print("\n\nList of pods on %s:" % cluster2)
    for i in client2.list_pod_for_all_namespaces().items:
        print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


def podConfigList():
    """
    Allows you to pick a context and then lists all pods in the chosen context. A
    context includes a cluster, a user, and a namespace.
    :return:
    """
    contexts, active_context = config.list_kube_config_contexts()
    if not contexts:
        print("Cannot find any context in kube-config file.")
        return
    contexts = [context['name'] for context in contexts]
    active_index = contexts.index(active_context['name'])
    option, _ = pick(contexts, title="Pick the context to load",
                     default_index=active_index)
    # Configs can be set in Configuration class directly or using helper
    # utility
    config.load_kube_config(context=option)

    print("Active host is %s" % configuration.Configuration().host)

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for item in ret.items:
        print(
            "%s\t%s\t%s" %
            (item.status.pod_ip,
             item.metadata.namespace,
             item.metadata.name))


def changeNodeLabel():
    """
    Changes the labels of the "minikube" node. Adds the label "foo" with value
    "bar" and will overwrite the "foo" label if it already exists. Removes the
    label "baz".
    :return:
    """
    body = {
        "metadata": {
            "labels": {
                "foo": "bar",
                "baz": None}
        }
    }
    api_response = v1.patch_node("minikube", body)
    pprint(api_response)


def configOutOfCluster():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


def pickKubeConfigContext():
    """
    Allows you to pick a context and then lists all pods in the chosen context.
    :return:
    """
    contexts, active_context = config.list_kube_config_contexts()
    if not contexts:
        print("Cannot find any context in kube-config file.")
        return
    contexts = [context['name'] for context in contexts]
    active_index = contexts.index(active_context['name'])
    option, _ = pick(contexts, title="Pick the context to load",
                     default_index=active_index)
    # Configs can be set in Configuration class directly or using helper
    # utility
    config.load_kube_config(context=option)

    print("Active host is %s" % configuration.Configuration().host)

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for item in ret.items:
        print(
            "%s\t%s\t%s" %
            (item.status.pod_ip,
             item.metadata.namespace,
             item.metadata.name))


def podExecCommands():
    """
    Shows the functionality of exec using a Busybox container.
    :return:
    """
    pass


if __name__ == "__main__":
    init()

    # filename = "hello-kubernetes.yaml"
    # createDeployment(filename)

