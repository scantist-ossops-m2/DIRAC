""" The Notification service provides a toolkit to contact people via email
    (eventually SMS etc.) to trigger some actions.

    The original motivation for this is due to some sites restricting the
    sending of email but it is useful for e.g. crash reports to get to their
    destination.

    Another use-case is for users to request an email notification for the
    completion of their jobs.  When output data files are uploaded to the
    Grid, an email could be sent by default with the metadata of the file.

    It can also be used to set alarms to be promptly forwarded to those
    subscribing to them.
"""
from DIRAC import S_ERROR, S_OK, gConfig
from DIRAC.ConfigurationSystem.Client import PathFinder
from DIRAC.Core.DISET.RequestHandler import RequestHandler
from DIRAC.Core.Security import Properties
from DIRAC.Core.Utilities.DictCache import DictCache
from DIRAC.Core.Utilities.Mail import Mail
from DIRAC.FrameworkSystem.DB.NotificationDB import NotificationDB


class NotificationHandlerMixin:
    @classmethod
    def initializeHandler(cls, serviceInfo):
        """Handler initialization"""

        cls.mailCache = DictCache()
        cls.notDB = NotificationDB()
        cls.notDB.purgeExpiredNotifications()

        return S_OK()

    ###########################################################################
    types_sendMail = [str, str, str, str]

    def export_sendMail(self, address, subject, body, fromAddress):
        """Send an email with supplied body to the specified address using the Mail utility.

        :param str address: recipient addresses
        :param str subject: subject of letter
        :param str body: body of letter
        :param str fromAddress: sender address, if "", will be used default from CS

        :return: S_OK(str)/S_ERROR() -- str is status message
        """
        self.log.verbose(f"Received signal to send the following mail to {address}:\nSubject = {subject}\n{body}")
        if self.mailCache.exists(hash(address + subject + body)):
            return S_OK("Email with the same content already sent today to current addresses, come back tomorrow")
        eMail = Mail()
        notificationSection = PathFinder.getServiceSection("Framework/Notification")
        csSection = notificationSection + "/SMTP"
        eMail._smtpHost = gConfig.getValue(f"{csSection}/Host")
        eMail._smtpPort = gConfig.getValue(f"{csSection}/Port")
        eMail._smtpLogin = gConfig.getValue(f"{csSection}/Login")
        eMail._smtpPasswd = gConfig.getValue(f"{csSection}/Password")
        eMail._smtpPtcl = gConfig.getValue(f"{csSection}/Protocol")
        eMail._subject = subject
        eMail._message = body
        eMail._mailAddress = address
        if fromAddress:
            eMail._fromAddress = fromAddress
        eMail._fromAddress = gConfig.getValue(f"{csSection}/FromAddress") or eMail._fromAddress
        result = eMail._send()
        if not result["OK"]:
            self.log.warn(f"Could not send mail with the following message:\n{result['Message']}")
        else:
            self.mailCache.add(hash(address + subject + body), 3600 * 24)
            self.log.info(f"Mail sent successfully to {address} with subject {subject}")
            self.log.debug(result["Value"])

        return result

    ###########################################################################
    # MANANGE ASSIGNEE GROUPS
    ###########################################################################

    types_setAssigneeGroup = [str, list]

    @classmethod
    def export_setAssigneeGroup(cls, groupName, userList):
        """Create a group of users to be used as an assignee for an alarm"""
        return cls.notDB.setAssigneeGroup(groupName, userList)

    types_getUsersInAssigneeGroup = [str]

    @classmethod
    def export_getUsersInAssigneeGroup(cls, groupName):
        """Get users in assignee group"""
        return cls.notDB.getUserAsignees(groupName)

    types_deleteAssigneeGroup = [str]

    @classmethod
    def export_deleteAssigneeGroup(cls, groupName):
        """Delete an assignee group"""
        return cls.notDB.deleteAssigneeGroup(groupName)

    types_getAssigneeGroups = []

    @classmethod
    def export_getAssigneeGroups(cls):
        """Get all assignee groups and the users that belong to them"""
        return cls.notDB.getAssigneeGroups()

    types_getAssigneeGroupsForUser = [str]

    def export_getAssigneeGroupsForUser(self, user):
        """Get all assignee groups and the users that belong to them"""
        credDict = self.getRemoteCredentials()
        if Properties.ALARMS_MANAGEMENT not in credDict["properties"]:
            user = credDict["username"]
        return self.notDB.getAssigneeGroupsForUser(user)

    ###########################################################################
    # MANAGE NOTIFICATIONS
    ###########################################################################

    types_addNotificationForUser = [str, str]

    def export_addNotificationForUser(self, user, message, lifetime=604800, deferToMail=True):
        """Create a group of users to be used as an assignee for an alarm"""
        try:
            lifetime = int(lifetime)
        except Exception:
            return S_ERROR("Message lifetime has to be a non decimal number")
        return self.notDB.addNotificationForUser(user, message, lifetime, deferToMail)

    types_removeNotificationsForUser = [str, list]

    def export_removeNotificationsForUser(self, user, notIds):
        """Get users in assignee group"""
        credDict = self.getRemoteCredentials()
        if Properties.ALARMS_MANAGEMENT not in credDict["properties"]:
            user = credDict["username"]
        return self.notDB.removeNotificationsForUser(user, notIds)

    types_markNotificationsAsRead = [str, list]

    def export_markNotificationsAsRead(self, user, notIds):
        """Delete an assignee group"""
        credDict = self.getRemoteCredentials()
        if Properties.ALARMS_MANAGEMENT not in credDict["properties"]:
            user = credDict["username"]
        return self.notDB.markNotificationsSeen(user, True, notIds)

    types_markNotificationsAsNotRead = [str, list]

    def export_markNotificationsAsNotRead(self, user, notIds):
        """Delete an assignee group"""
        credDict = self.getRemoteCredentials()
        if Properties.ALARMS_MANAGEMENT not in credDict["properties"]:
            user = credDict["username"]
        return self.notDB.markNotificationsSeen(user, False, notIds)

    types_getNotifications = [dict, list, int, int]

    def export_getNotifications(self, selectDict, sortList, startItem, maxItems):
        """Get all assignee groups and the users that belong to them"""
        credDict = self.getRemoteCredentials()
        if Properties.ALARMS_MANAGEMENT not in credDict["properties"]:
            selectDict["user"] = [credDict["username"]]
        return self.notDB.getNotifications(selectDict, sortList, startItem, maxItems)


class NotificationHandler(NotificationHandlerMixin, RequestHandler):
    pass
