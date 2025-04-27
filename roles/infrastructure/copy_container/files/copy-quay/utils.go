package main

import (
    "bufio"
    "encoding/json"
    "fmt"
    "html/template"
    "io/ioutil"
    "net/http"
    "os"
    "regexp"
    "time"

    "github.com/sirupsen/logrus"
)

// Build - Basic struct returned by zuul api in json format
type Build struct {
    Status string `json:"result"`
    URL    string `json:"log_url"`
}

type ParsedBuiltContainerLogLine struct {
	repository string
	tag        string
	digest     string
}
type ParsedBuiltContainerLogLines []*ParsedBuiltContainerLogLine

func writeHTLMReport(success []string, failed []string, hash string, output string) {
    var reportTemplate = template.Must(template.New("report").Parse(`
    <!DOCTYPE html>
    <html>
    <head>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
          integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T"
          crossorigin="anonymous">
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"
            integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM"
            crossorigin="anonymous">
    </script>
    </head>
    <body>
    <h2>Report latest containers</h2>
    <h3>Latest hash: {{.Hash}}</h3>
    <h3>Date: {{.Today.Format "01-02-2006 15:04"}}</h3>
    <h4>Failing: {{.Failing}}</h4>
    <h4>Passing: {{.Passing}}</h4>
    <table class="table table-hover">
    <thead>
        <tr>
        <th>Container Name</th>
        <th>Status</th>
        </tr>
    </thead>
    <tbody>
    {{range .Items}}
        {{ if eq .ContainerStatus "SUCCESS" }}
        <tr class="table-success">
        {{ else }}
        <tr class="table-danger">
        {{ end }}
        <td>{{.ContainerName}}</td>
        <td>{{.ContainerStatus}}</td>
        </tr>
        <tr>
    {{end}}
    </tbody>
    </table>
    </body>
    </html>
    `))

    type Containers struct {
        ContainerName string
        ContainerStatus string
    }

    type Data struct {
        Items []*Containers
        Hash string
        Today time.Time
        Passing int
        Failing int
    }

    data := new(Data)
    data.Hash = hash
    data.Today = time.Now()
    data.Passing = len(success)
    data.Failing = len(failed)

    for _, container := range(success) {
        item := new(Containers)
        item.ContainerName = container
        item.ContainerStatus = "SUCCESS"
        data.Items = append(data.Items, item)
    }
    for _, container := range(failed) {
        item := new(Containers)
        item.ContainerName = container
        item.ContainerStatus = "FAILURE"
        data.Items = append(data.Items, item)
    }

    file, err := os.Create(output)
    if err != nil {
        logrus.Errorln("Failed to create HTML report file")
    }
    writer := bufio.NewWriter(file)
    if err := reportTemplate.Execute(writer, data); err != nil {
        writer.Flush()
        logrus.Fatal(err)
    }
    writer.Flush()
}

func getLatestGoodBuildURL(jobName string, opts *globalOptions) string {

    url := fmt.Sprintf("%sbuilds?job_name=%s", opts.zuulAPI, jobName)
    response, err := http.Get(url)
    var builds []Build

    if err != nil {
        logrus.Errorln("The HTTP request failed with error ", err)
    } else {
        data, _ := ioutil.ReadAll(response.Body)
        if err := json.Unmarshal(data, &builds); err != nil {
            logrus.Errorln("The unmarshal failed with error ", err)
        }
    }
    for _, build := range builds {
        if build.Status == "SUCCESS" {
            return build.URL
        }
    }
    return ""
}

func _fetch_(URL string) (string, error) {
    request, err := http.NewRequest(http.MethodGet, URL, nil)
    if err != nil {
        logrus.Errorln("The HTTP request failed with error ", err)
        return "", err
    }

    client := &http.Client{}
    response, err := client.Do(request)
    if err != nil {
        logrus.Errorln("Failed to get response from the HTTP request")
        return "", err
    }
    if response.StatusCode == 404 {
        msg := fmt.Sprintf("URL %s not found", URL)
        logrus.Errorln(msg)
        return "", fmt.Errorf(msg)
    }

    data, err := ioutil.ReadAll(response.Body)
    if err != nil {
        logrus.Errorln("Failed to read Body content")
        return "", err
    }
    return string(data), nil
}

func _fetch(URL string) (string, error) {
    response, err := http.Get(URL)
    if err != nil {
        logrus.Errorln("The HTTP request failed with error ", err)
        return "", err
    }
    if response.StatusCode == 404 {
        msg := fmt.Sprintf("URL not found: %s", URL)
        logrus.Errorln(msg)
        return "", fmt.Errorf(msg)
    }
    data, err := ioutil.ReadAll(response.Body)
    if err != nil {
        logrus.Errorln("Failed to read Body content")
        return "", err
    }
    return string(data), nil
}

func fetchLogs(URL string) string {
    // There are three different places where we can get the list of
    // containers...
    path := fmt.Sprintf("%slogs/containers-successfully-built.log", URL)
    data, _ := _fetch(path)

    if data == "" {
        path = fmt.Sprintf("%slogs/containers-built.log", URL)
        data , _ = _fetch(path)
    }

    if data == "" {
        path = fmt.Sprintf("%sci-framework-data/logs/containers-built.log", URL)
        data , _ = _fetch(path)
    }

    if data == "" {
        path = fmt.Sprintf("%sjob-output.txt", URL)
        data, _ = _fetch(path)
    }
    logrus.Info("Fetching logs in ", path)
    return data
}

func repoExists(repoName string, repositories []Container) bool {
    for _, container := range repositories {
        if container.Name == repoName {
            return true
        }
    }
    return false
}

func getCurrentTripleoRepo(api string) string {

    type DlrnApiResponse struct {
        PromoteName   string `json:"promote_name"`
        RepoHash      string `json:"repo_hash"`
        AggregateHash string `json:"aggregate_hash"`
        CommitHash    string `json:"commit_hash"`
    }

    var returnApi []DlrnApiResponse

    apiEndpoint := "api/promotions?promote_name=current-tripleo&limit=1"
    apiUrl := fmt.Sprintf("%s/%s", api, apiEndpoint)

    response, err := http.Get(apiUrl)

    if err != nil {
        logrus.Errorln("The HTTP request failed with error ", err)
    } else {
        data, _ := ioutil.ReadAll(response.Body)
        if err := json.Unmarshal(data, &returnApi); err != nil {
            logrus.Errorln("The unmarshal failed with error ", err)
        }
    }
    if len(returnApi) > 0 {
        if returnApi[0].AggregateHash != "" {
            return returnApi[0].AggregateHash
        }
        return returnApi[0].RepoHash
    }

    return ""
}

func parseLog(data string) ParsedBuiltContainerLogLines {
	var parsedLogLines ParsedBuiltContainerLogLines
	r, _ := regexp.Compile(`(?m)\/([\w-]+)\s+([\w_]+)\s+([\w]+)`)
	for _, matches := range r.FindAllStringSubmatch(data, -1) {
		parsedLogLines = append(parsedLogLines, &ParsedBuiltContainerLogLine{
			repository: matches[1],
			tag:        matches[2],
			digest:     matches[3],
		})
	}
	return parsedLogLines
}
