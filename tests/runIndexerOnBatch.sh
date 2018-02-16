#!/bin/sh

. runIndexerConfig.sh

export GP_METADATA_DIR=$WORKING_DIR/metaLocal

. ../container/common/testing_scripts/runOnBatch.sh

