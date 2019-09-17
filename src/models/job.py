class Job:
    def __init__(self, title, location, company, joblink, description, publishdate):
        self.title = title
        self.company = company
        self.location = location
        self.publishdate = publishdate
        self.description = description
        self.joblink = joblink

    def __str__(self):
        return str(
            "{0:20}".format(self.title) + " | " + "Company: " + self.company + " | " + "Location: " + self.location)

    def __eq__(self, other):
        return self.description == other.description

    def __hash__(self):
        return hash(('description', self.description))

    def as_dict(self):
        return {'title': self.title, 'company': self.company,
                'location': self.location, 'publishdate': self.publishdate,
                'description': self.description, 'joblink': self.joblink}