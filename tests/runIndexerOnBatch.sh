#!/bin/sh

. runIndexerConfig.sh

export GP_METADATA_DIR=$WORKING_DIR/metaLocal

. ../common/testing_scripts/runOnBatch.sh

