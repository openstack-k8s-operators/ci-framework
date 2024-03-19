package main

import (
    "fmt"

    "github.com/sirupsen/logrus"
    "github.com/spf13/cobra"
)

type tagOptions struct {
    global *globalOptions
    tag string
    tag_sha bool
    hash string
    htmlOutput string
}


var optsTag = &tagOptions{}

func tagCmd(global *globalOptions) *cobra.Command {
    optsTag.global = global

    cmd := &cobra.Command{
        Use:   "tag [CONTAINER NAME]",
        Short: "Tag images",
        RunE: optsTag.run,
    }
    cmd.Flags().StringVar(&optsTag.tag, "tag", "current-podified", "Image tag name")
    cmd.Flags().StringVar(&optsTag.hash, "force-hash", "", "Force an specific hash, overwriting delorean api")
    cmd.Flags().StringVar(&optsTag.htmlOutput, "html", "", "HTML output report file")
    cmd.Flags().BoolVar(&optsTag.tag_sha, "tag-sha", true, "Should also tag sha. Default to true")
    return cmd
}

func (opts *tagOptions) run(cmd *cobra.Command, args []string) error {

    var urlApi = opts.global.Entry.Api

    if urlApi == "" {
        return fmt.Errorf("invalid release")
    }

    var promoted_hash = ""
    if opts.hash != "" {
        logrus.Info("Overwriting promoted hash")
        promoted_hash = opts.hash
    } else {
        promoted_hash = getCurrentTripleoRepo(urlApi)
    }

    logrus.Infoln("Promoted hash: ", promoted_hash)
    if len(args) > 0 {
        for _, image := range args {
            sha, err := getImageManifest(opts.global.toNamespace, image, promoted_hash)
            if err != nil {
                logrus.Errorln("Unable to get image manifest: ", err)
            } else {
                tagImage(opts.global.toNamespace, image, opts.tag, sha)
                if opts.tag_sha {
                    tagImage(opts.global.toNamespace, image, sha[7:], sha)
                }
            }
        }
    } else {
        image := getLatestGoodBuildURL(opts.global.job, opts.global)
        data := fetchLogs(image)
        parsedLogLines := parseLog(data)

        logrus.Infof("image: %s namespace: %s promoted_hash: %s", image, opts.global.toNamespace, promoted_hash)
        failed_tag := make([]string, 0)
        success_tag := make([]string, 0)
        for _, parsedLine := range parsedLogLines {
            sha, err := getImageManifest(opts.global.toNamespace, parsedLine.repository, promoted_hash)
            if err != nil {
                logrus.Errorln("Unable to get image manifest: ", err)
            } else {
                if err := tagImage(opts.global.toNamespace, parsedLine.repository, opts.tag, sha); err != nil {
                    failed_tag = append(failed_tag, parsedLine.repository)
                } else {
                    success_tag = append(success_tag, parsedLine.repository)
                    if opts.tag_sha {
                        tagImage(opts.global.toNamespace, parsedLine.repository, sha[7:], sha)
                    }
                }
            }
        }
        if opts.htmlOutput != "" {
            writeHTLMReport(success_tag, failed_tag, promoted_hash, opts.htmlOutput)
        }
    }
    return nil
}
