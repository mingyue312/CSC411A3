from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime
import os.path
import time

import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

import cifar10

# import cifar10_eval

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string('train_dir', '/tmp/cifar10_train',
                           """Directory where to write event logs """
                           """and checkpoint.""")
tf.app.flags.DEFINE_integer('max_steps', 20000,
                            """Number of batches to run.""")
tf.app.flags.DEFINE_boolean('log_device_placement', False,
                            """Whether to log device placement.""")


def train():
    """Train CIFAR-10 for a number of steps."""
    with tf.Graph().as_default():
        global_step = tf.Variable(0, trainable=False)

        # Get images and labels for CIFAR-10.
        images, labels = cifar10.distorted_inputs()
        # avg = tf.reduce_mean(labels)

        # Build a Graph that computes the logits predictions from the
        # inference model.
        logits = cifar10.inference(images, dropout=0.8, reuse=False)

        # Calculate loss.
        loss = cifar10.loss(logits, labels)

        # calculate accuracy for training set
        acc = cifar10.accuracy(logits, labels)

        # Build a Graph that trains the model with one batch of examples and
        # updates the model parameters.
        train_op = cifar10.train(loss, global_step)

        # Setup cross validation right here
        # get a batch of xvalidation images
        # eval_data=False: use cross validation, not test test set
        val_images, val_labels = cifar10.inputs(eval_data=False)

        val_logits = cifar10.inference(val_images, dropout=1, reuse=True)

        top_k_op = tf.nn.in_top_k(val_logits, val_labels, 1)

        # Create a saver.
        saver = tf.train.Saver(tf.all_variables())

        # Build the summary operation based on the TF collection of Summaries.
        summary_op = tf.merge_all_summaries()

        # Build an initialization operation to run below.
        init = tf.initialize_all_variables()

        # Start running operations on the Graph.
        sess = tf.Session(config=tf.ConfigProto(
            log_device_placement=FLAGS.log_device_placement))
        sess.run(init)

        # Start the queue runners.
        tf.train.start_queue_runners(sess=sess)

        summary_writer = tf.train.SummaryWriter(FLAGS.train_dir, sess.graph)

        for step in xrange(FLAGS.max_steps):
            start_time = time.time()
            _, loss_value, acc_value = sess.run([train_op, loss, acc])
            duration = time.time() - start_time

            assert not np.isnan(loss_value), 'Model diverged with loss = NaN'

            if step % 10 == 0:
                num_examples_per_step = FLAGS.batch_size
                examples_per_sec = num_examples_per_step / duration
                sec_per_batch = float(duration)
                format_str = ('%s: step %d, loss = %.2f, acc = %.2f (%.1f examples/sec; %.3f '
                              'sec/batch)')
                print(format_str % (datetime.now(), step, loss_value, acc_value,
                                    examples_per_sec, sec_per_batch))

            if step % 100 == 0:
                summary_str = sess.run(summary_op)
                summary_writer.add_summary(summary_str, step)

            # Save the model checkpoint periodically.
            if step % 100 == 0 or (step + 1) == FLAGS.max_steps:
                checkpoint_path = os.path.join(FLAGS.train_dir, 'model.ckpt')
                saver.save(sess, checkpoint_path, global_step=step)
                # run the xvalidation
                prediction = sess.run([top_k_op])
                precision = np.sum(prediction) / FLAGS.batch_size
                print(("At step %d cross validation precision: %.3f") % (step, precision))


def main(argv=None):  # pylint: disable=unused-argument
    # cifar10.maybe_download_and_extract()
    if tf.gfile.Exists(FLAGS.train_dir):
        tf.gfile.DeleteRecursively(FLAGS.train_dir)
    tf.gfile.MakeDirs(FLAGS.train_dir)
    train()


if __name__ == '__main__':
    tf.app.run()
