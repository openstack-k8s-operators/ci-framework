package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	"gopkg.in/jcmturner/gokrb5.v7/client"
	"gopkg.in/jcmturner/gokrb5.v7/config"
	"gopkg.in/jcmturner/gokrb5.v7/keytab"
	"gopkg.in/jcmturner/gokrb5.v7/spnego"
)

const (
	krb5ConfPath = "/etc/krb5.conf"      // Path to your krb5.conf file
	keytabPath   = "/home/poojajadhav/Downloads/osp-ci-promoter.keytab"
	realm        = "ipa.redhat.com"       // Replace with your Kerberos realm
	username     = "osp-ci-promoter"
	url          = "https://sf.apps.int.gpc.ocp-hub.prod.psi.redhat.com/zuul/api/tenant/components-integration/builds?job_name=periodic-container-tcib-build-push-upload-rhel-9-rhos-18"
)

func main() {
	// Load Kerberos configuration
	krb5Conf, err := config.Load(krb5ConfPath)
	fmt.Println("krb5 conf*********************", krb5Conf)
	if err != nil {
		log.Fatalf("Failed to load krb5.conf: %v", err)
	}

	kt, err := keytab.Load(keytabPath)
	if err != nil {
		log.Fatalf("Failed to load keytab: %v",err)
	}

	// Create a new Kerberos client using a keytab file
	krbClient := client.NewClientWithKeytab(username, realm, kt, krb5Conf)
	if err != nil {
		log.Fatalf("Failed to create Kerberos client: %v", err)
	}

	// Perform krbClient authentication
	err = krbClient.Login()
	if err != nil {
		log.Fatalf("Kerberos login failed: %v", err)
	}

	// Create an SPNEGO HTTP client
	spnegoClient := spnego.NewClient(krbClient, nil, "")

	// Create an HTTP GET request
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		log.Fatalf("Failed to create request: %v", err)
	}

	// Execute the request with SPNEGO authentication
	resp, err := spnegoClient.Do(req)
	if err != nil {
		log.Fatalf("HTTP request failed: %v", err)
	}
	defer resp.Body.Close()

	// Read and print response body
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Fatalf("Failed to read response: %v", err)
	}

	fmt.Printf("Response Status: %s\n", resp.Status)
	fmt.Printf("Response Body:\n%s\n", string(body))
}

