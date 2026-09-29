package unit

import (
	"testing"

	"go-framework-guap/core/utils"
)

func TestSetLevelDoesNotPanic(t *testing.T) {
	utils.SetLevel(utils.DEBUG)
	utils.SetLevel(utils.INFO)
	utils.SetLevel(utils.WARN)
	utils.SetLevel(utils.ERROR)
}

func TestLogFunctionsDoNotPanic(t *testing.T) {
	// Level INFO means Debug is suppressed; calling every level must be safe.
	utils.SetLevel(utils.DEBUG)
	utils.Debug("debug %d", 1)
	utils.Info("info %s", "x")
	utils.Warn("warn")
	utils.Error("error")
}