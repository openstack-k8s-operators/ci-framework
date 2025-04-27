package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"

	"github.com/sirupsen/logrus"
)

// Container - Basic struct to return list of repositories
type Container struct {
	Name string `json:"name"`
}

// Repositories - Basic struct to return list of repositories
type Repositories struct {
	Repositories []Container `json:"repositories"`
}

func createNewRepository(baseUrl, namespace, containerName string) (string, error) {
    logrus.Info(fmt.Sprintf("Creating new repository %s/%s", namespace, containerName))
	requestBody, err := json.Marshal(map[string]string{
		"namespace":   namespace,
		"repository":  containerName,
		"description": "Container image " + containerName,
		"visibility":  "public",
	})
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("POST", fmt.Sprintf("%s/repository", baseUrl), bytes.NewBuffer(requestBody))

	if err != nil {
		return "", err
	}
	var bearer = "Bearer " + opts.token
	req.Header.Add("Authorization", bearer)
	req.Header.Set("Content-Type", "application/json")

	client := http.Client{}
	resp, err := client.Do(req)

	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	data, _ := ioutil.ReadAll(resp.Body)
	return string(data), nil
}

func tagExists(baseUrl, namespace, repositoryName, tag string) bool {
	url := fmt.Sprintf("%s/repository/%s/%s/tag/?specificTag=%s", baseUrl, namespace, repositoryName, tag)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return false
	}
	var bearer = "Bearer " + opts.token
	req.Header.Add("Authorization", bearer)
	req.Header.Add("Accept", "application/json")

	client := http.Client{}

	resp, err := client.Do(req)
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	data, _ := ioutil.ReadAll(resp.Body)

	obj := map[string]interface{}{}
	if err := json.Unmarshal([]byte(data), &obj); err != nil {
		return false
	}

	if obj["images"] != nil {
		return true
	}
	return true
}

func imageWithDigestExists(baseUrl, namespace, repositoryName, tag, imageDigest string) bool {
	if digest, err := getImageManifest(baseUrl, namespace, repositoryName, tag); err != nil {
		if strings.HasPrefix(digest, fmt.Sprintf("sha256:%s", imageDigest)) {
			return true
		}
	}
	return false
}

func getImageManifest(baseUrl, namespace, repositoryName, specificTag string) (string, error) {
	url := fmt.Sprintf("%s/repository/%s/%s/tag/?specificTag=%s", baseUrl, namespace, repositoryName, specificTag)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {

	}
	var bearer = "Bearer " + opts.token
	req.Header.Add("Authorization", bearer)
	req.Header.Add("Accept", "application/json")

	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
	}
	defer resp.Body.Close()

	type ListTags struct {
		Digest string `json:"manifest_digest"`
	}
	type Tag struct {
		Tags []ListTags `json:"tags"`
	}

	data, _ := ioutil.ReadAll(resp.Body)

	var obj Tag

	if err := json.Unmarshal([]byte(data), &obj); err != nil {
		return "", err
	}
	if len(obj.Tags) > 0 {
		return obj.Tags[0].Digest, nil
	}
	return "", fmt.Errorf("Manifest digest for given image was not found")
}

func tagImage(baseUrl, namespace, repositoryName, tag, manifestDigest string)  error {
    logrus.Info(fmt.Sprintf("Tagging %s/%s with tag %s and manifest %s", namespace, repositoryName, tag, manifestDigest))
	url := fmt.Sprintf("%s/repository/%s/%s/tag/%s", baseUrl, namespace, repositoryName, tag)

	requestBody, err := json.Marshal(map[string]string{
		"manifest_digest": manifestDigest,
	})

	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodPut, url, bytes.NewBuffer(requestBody))
	if err != nil {
		return err
	}
	client := http.Client{}
	var bearer = "Bearer " + opts.token
	req.Header.Add("Authorization", bearer)
	req.Header.Add("Accept", "application/json")
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	data, _ := ioutil.ReadAll(resp.Body)
	fmt.Println(string(data))
	return nil
}

func listRepositories(baseUrl, namespace string) ([]Container, error) {
	url := fmt.Sprintf("%s/repository?private=false&public=true&namespace=%s", baseUrl, namespace)
	req, err := http.NewRequest("GET", url, nil)

	if err != nil {
		return nil, err
	}
	var bearer = "Bearer " + opts.token
	req.Header.Add("Authorization", bearer)
	req.Header.Add("Accept", "application/json")

	client := http.Client{}

	var repo Repositories

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	data, _ := ioutil.ReadAll(resp.Body)
	if err := json.Unmarshal(data, &repo); err != nil {
		return nil, err
	}
	return repo.Repositories, nil
}
