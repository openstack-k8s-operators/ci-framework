package main

import (
    "fmt"

    "os"

    "github.com/containers/image/v5/copy"
    "github.com/containers/image/v5/manifest"
    "github.com/containers/image/v5/transports/alltransports"
    "github.com/sirupsen/logrus"
    "github.com/spf13/cobra"
)

type copyOptions struct {
    global *globalOptions
    htmlOutput string
}

var optsCopy = &copyOptions{}

func copyCmd(global *globalOptions) *cobra.Command {
    optsCopy.global = global

    cmd := &cobra.Command{
        Use:   "copy [CONTAINER NAME]",
        Short: "Copy images from source to destiny",
        RunE:  optsCopy.run,
    }
    cmd.Flags().StringVar(&optsCopy.htmlOutput, "html", "", "HTML output report file")
    return cmd
}

func (opts *copyOptions) run(cmd *cobra.Command, args []string) error {
    if len(args) > 0 {
        if opts.global.hash == "" {
            return fmt.Errorf("you must specify a hash if you are copying specific images")
        }

        tagToPush := opts.global.hash
        for _, image := range args {
            if(opts.global.pushHash != "") {
                tagToPush = opts.global.pushHash
            }
            if tagExists(opts.global.quayApiBaseUrl, opts.global.toNamespace, image, tagToPush) {
                return fmt.Errorf("Tag %s already exist on the destination namespace", tagToPush)
            }

            from := fmt.Sprintf("docker://%s/%s/%s:%s", opts.global.pullRegistry, opts.global.fromNamespace, image, opts.global.hash)
            to := fmt.Sprintf("docker://%s/%s/%s:%s", opts.global.pushRegistry, opts.global.toNamespace, image, tagToPush)
            if _, err := copyImage(from, to); err != nil {
                msg := fmt.Sprintf("Failed to copy container %s: %v", image, err)
                logrus.Errorln(msg)
            }
        }
    } else {
        image := getLatestGoodBuildURL(opts.global.job, opts.global)
        data := fetchLogs(image)
        parsedLogLines := parseLog(data)

        repositories, err := listRepositories(opts.global.quayApiBaseUrl, opts.global.toNamespace)

        failed_push := make([]string, 0)
        success_pushed := make([]string, 0)

        if err != nil {
            logrus.Error("Failed to fetch list of repositories ", err)
        }
        tagToPush := ""
        for _, parsedLine := range parsedLogLines {
            tagToPull := parsedLine.tag
            if(opts.global.hash != "") {
                tagToPull = opts.global.hash
            }
            tagToPush = tagToPull
            logrus.Debugln("Tag is: ", opts.global.pushHash)
            if(opts.global.pushHash != "") {
                tagToPush = opts.global.pushHash
                logrus.Debugln("Tag to push: ", tagToPush)
            }
            logrus.Info(fmt.Sprintf("Copying image %s/%s:%s", opts.global.toNamespace, parsedLine.repository, tagToPull))
            if !repoExists(parsedLine.repository, repositories) {
                _, err := createNewRepository(opts.global.quayApiBaseUrl, opts.global.toNamespace, parsedLine.repository)
                if err != nil {
                    logrus.Errorln("Failed to create repository: ", err)
                    continue
                }
            }

            if imageWithDigestExists(opts.global.quayApiBaseUrl, opts.global.toNamespace, parsedLine.repository, tagToPush, parsedLine.digest) {
                logrus.Errorf("Image with digest %s already exists on the destination namespace\n", parsedLine.digest)
                continue
            }
            // from := fmt.Sprintf("docker://%s/%s/%s:current-tripleo", opts.global.pullRegistry, opts.global.fromNamespace, parsedLine.Repository)
            from := fmt.Sprintf("docker://%s/%s/%s:%s", opts.global.pullRegistry, opts.global.fromNamespace, parsedLine.repository, tagToPull)
            to := fmt.Sprintf("docker://%s/%s/%s:%s", opts.global.pushRegistry, opts.global.toNamespace, parsedLine.repository, tagToPush)
            _, err := copyImage(from, to)
            if err != nil {
                failed_push = append(failed_push, parsedLine.repository)
                logrus.Errorln("Failed to copy container image: ", err)
            } else {
                success_pushed = append(success_pushed, parsedLine.repository)
            }
        }

        if(opts.htmlOutput != "") {
            writeHTLMReport(success_pushed, failed_push, tagToPush, opts.htmlOutput)
        }
    }

    return nil
}

func copyImage(from, to string) (string, error) {

    logrus.Debug(fmt.Sprintf("Copying container image %s to %s", from, to))
    srcRef, err := alltransports.ParseImageName(from)
    if err != nil {
        return "", fmt.Errorf("Failed to parse image %s to be pulled from: %v", from, err)
    }

    destRef, err := alltransports.ParseImageName(to)
    if err != nil {
        return "", fmt.Errorf("Failed to parse image %s to be pushed to: %v", to, err)
    }

    policyContext, err := optsCopy.global.getPolicyContext()
    if err != nil {
        return "", fmt.Errorf("Failed to get policy context: %v", err)
    }

    ctx, cancel := optsCopy.global.commandTimeoutContext()
    defer cancel()

    sourceCtx := optsCopy.global.newSystemContext()
    destinationCtx := optsCopy.global.newImageDestSystemContext()

    man, err := copy.Image(ctx, policyContext, destRef, srcRef, &copy.Options{
        RemoveSignatures:      true,
        SignBy:                "",
        ReportWriter:          os.Stdin,
        SourceCtx:             sourceCtx,
        DestinationCtx:        destinationCtx,
        ForceManifestMIMEType: manifest.DockerV2Schema2MediaType,
        ImageListSelection:    copy.CopyAllImages,
    })
    if err != nil {
        return "", fmt.Errorf("Error in copy the image: %v", err)
    }
    logrus.Debugln("Image copied successfully")

    return string(man), nil
}
