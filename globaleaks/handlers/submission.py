# -*- coding: UTF-8
#   submission
#   **********
#   :copyright: 2012 Hermes No Profit Association - GlobaLeaks Project
#   :author: Claudio Agosti <vecna@globaleaks.org>, Arturo Filastò <art@globaleaks.org>
#   :license: see LICENSE
#
#   Implements a GlobaLeaks submission.
import json

from twisted.python import log
from twisted.internet.defer import returnValue, inlineCallbacks

from globaleaks import models
from globaleaks.utils import idops

from globaleaks import messages

from globaleaks.rest.errors import GLErrorCode
from globaleaks.handlers.base import BaseHandler

from globaleaks.models.base import ModelError

from cyclone.web import asynchronous, HTTPError

from globaleaks import messages

def mydirtydebug(whoami, safereq, uriargs, args, kw):
    print "[:>]", whoami, safereq, type(uriargs), uriargs, args, kw

class SubmissionRoot(BaseHandler):
    @asynchronous
    @inlineCallbacks
    def get(self, *uriargs):
        """
        This creates an empty submission and returns the ID
        to be used when referencing it as a whistleblower.
        sessionID is defined in recurringtypes, and is a 50byte random string.
            * Response:
              Status Code: 200 (OK)
              {
                  'submission_id': 'sessionID',
                  'creation_time': 'Time'
              }
              Status code: 201 (Created)
        """
        # XXX do sanitization and validation here
        self.set_status(201)

        submission = models.submission.Submission()

        #fake_submission = requests.submissionStatusPost
        #new_submission.fields = fake_submission['fields']

        #fake_receivers = [idops.random_receiver_id(),
        #                  idops.random_receiver_id(),
        #                  idops.random_receiver_id(),
        #                  idops.random_receiver_id()]
        #new_submission.receivers = fake_receivers

        output = yield submission.new()

        self.write(output)
        self.finish()
        # dummy.SUBMISSION_NEW_GET(output)

class SubmissionStatus(BaseHandler):
    """
    This interface represent the state of the submission. Will show the current
    uploaded data, choosen group, and file uploaded.

    permit to update fields content and group selection.
    """
    @asynchronous
    @inlineCallbacks
    def get(self, submission_id):
        """
        Returns the currently submitted fields, selected group, and uploaded files.
        * Response:
          {
            'fields': [ '$formFieldsDict' ],
            'receivers_selected': [ '$receiverDescriptionDict' ],
            'creation_time': 'Time'
          }
        """
        submission = models.submission.Submission()
        status = yield submission.status(submission_id)

        self.set_status(200)
        self.write(status)
        self.finish()

    """
    status handle the group receiver selection
        (if enabled in the context settings)
    handle the fields submission
        (import the fields in the temporary submission_id entry)
    """

    #messageTypes['post'] = messages.base.fileDict
    def post(self, submission_id, *uriargs):
        """
        * Request:
          {
            'fields': [ '$formFieldsDict' ]
            'receiver_selected': [ 'receiverID', 'receiverID' ]
          }

        * Response:
          Status Code: 202 (accepted)

        * Error handling:
          As per "common behaviour in /submission/<submission_$ID/*"
          If receiver ID is invalid:
            { 'error_code': 'Int', 'error_message': 'receiver selected ID is invalid' }
          a receiver ID is invalid if:
            . receiver do not match in the context
          If the property of "receiver selection" is not set, the receiver_selected value
          is IGNORED.
        """
        #request = messages.validateMessage(self.request.body,
        #                            messages.requests.submissionStatus)

        request = json.loads(self.request.body)

        submission = models.submission.Submission()
        if not request:
            self.set_status(400)
            return

        if 'fields' in request and request['fields']:
            print "Updating fields with %s" % request
            submission.update_fields(submission_id, request['fields'])

        if 'context_selected' in request and request['context_selected']:
            print "Updating context with %s" % request
            submission.select_context(submission_id, request['context_selected'])

        self.set_status(202)


class SubmissionFinalize(BaseHandler):
    @asynchronous
    @inlineCallbacks
    def post(self, submission_id, *uriargs):
        """
        checks if all the 'Required' fields are present, then
        completes the submission in progress and returns a receipt.
        The WB may propose a receipt (because is a personal secret
        like a password, afterall)

        * Request (optional, see "Rensponse Variant" below):
          {
            'proposed-receipt': 'string'
            'folder_name': 'string'
            'folder_description': 'string'
          }

        * Response (HTTP code 412, Precondition Failed):
          If one of the fileDict is not complete, the finalize can't be performed.
          { 'error_code': 'Int', 'error_message': 'The upload appears not yet complete' }

        * Response (HTTP code 200):
          If the receipt is acceptable with the node requisite (minimum length
          respected, lowecase/uppercase, and other detail that need to be setup
          during the context configuration), i saved as authenticative secret for
          the WB Tip, is echoed back to the client Status Code: 201 (Created)

          Status Code: 200 (OK)
          { 'receipt': 'string (with receipt EQUAL to proposed-receipt)' }

        * Response (HTTP code 201):
          If the receipt do not fit node prerequisite, or is missing,
          the submission is finalized, and the server create a receipt.
          The client print back the receipt to the WB.

          Status Code: 201 (Created)
          { 'receipt': 'string' }

        Both response finalize the submission and the only difference is in the
        HTTP return code. This has been discussed (or would be discussed)
        [issue #19, Receipt, proposal of expansion](https://github.com/globaleaks/GLBackend/issues/19)
        * Error handling:
          As per "common behaviour in /submission/<submission_$ID/*"

          If the field check fail
          Status Code: 406 (Not Acceptable)
          { 'error_code': 'Int', 'error_message': 'fields requirement not respected' }

        """
        receipt_id = unicode(idops.random_receipt_id())

        submission = models.submission.Submission()
        try:
            yield submission.create_tips(submission_id, receipt_id)
        except ModelError, e:
            self.set_status(412)
            log.err("Error in finalize submission")
            log.err(e)
            # XXX add here errors and such
            self.finish()
            return

        self.set_status(201)

        receipt = {"receipt": receipt_id}
        self.write(receipt)
        self.finish()
