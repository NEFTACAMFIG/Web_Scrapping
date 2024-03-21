import scrapy

class LinkedInPeopleProfile(scrapy.Spider):
    name = "linkedin_people_profile"

    #custom_settings = {
    #    'FEEDS': {'data/%(name)s_%(time)s.jsonl': {'format': 'jsonlines',}}
    #}

    def start_requests(self):
        profile_list = ['reidhoffman']
        for profile in profile_list:
            linkedin_people_url = f'https://www.linkedin.com/in/{profile}/'
            yield scrapy.Request(url=linkedin_people_url, callback=self.parse_profile,
                                 meta={'profile': profile, 'linkedin_url': linkedin_people_url})

    def parse_profile(self, response):
        item = {}
        item['profile'] = response.meta['profile']
        item['url'] = response.meta['linkedin_url']

        # Experience Section
        item['experience'] = []
        experience_blocks = response.css('li.experience-item')
        for block in experience_blocks:
            experience = {}
            experience['organisation_profile'] = block.css('h4 a::attr(href)').get(default='').split('?')[0]

            experience['location'] = block.css('p.experience-item__location::text').get(default='').strip()

            # experience
            try:
                experience['description'] = block.css('p.show-more-less-text__text--more::text').getall()
            except Exception as e:
                print('experience --> description', e)
                try:
                    experience['description'] = block.css('p.show-more-less-text__text--less::text').getall()
                except Exception as e:
                    print('experience --> description', e)
                    experience['description'] = ''

            # time range
            try:
                date_ranges = block.css('span.date-range time::text').getall()
                if len(date_ranges) == 2:
                    experience['start_time'] = date_ranges[0]
                    experience['end_time'] = date_ranges[1]
                    experience['duration'] = block.css('span.date-range__duration::text').get()
                elif len(date_ranges) == 1:
                    experience['start_time'] = date_ranges[0]
                    experience['end_time'] = 'present'
                    experience['duration'] = block.css('span.date-range__duration::text').get()
            except Exception as e:
                print('experience --> time ranges', e)
                experience['start_time'] = ''
                experience['end_time'] = ''
                experience['duration'] = ''

            item['experience'].append(experience)




        # Education Section
        item['education'] = []
        education_blocks = response.css('li.education__list-item')
        for block in education_blocks:
            education = {}

            education['organisation'] = block.css('h3.profile-section-card__title a::text').get(default='').strip()

            education['organization_profile'] = block.css('a::attr(href)').get(default='').split('?')[0]

            try:
                education['course_details'] = ''
                for text in block.css('h4 span::text').getall():
                    education['course_details'] = education['course_details'] + text.strip() + ' '
                education['course_details'] = education['course_details'].strip()
            except Exception as e:
                print('education --> course details', e)
                education['course_details'] = ''

            # description
            education['description'] = block.css('div.education__item--details p::text').get(default='').strip()

            # time range
            try:
                date_ranges = block.css('span.date-range time::text').getall()
                if len(date_ranges) == 2:
                    education['start_time'] = date_ranges[0]
                    education['end_time'] = date_ranges[1]
                elif len(date_ranges) == 1:
                    education['start_time'] = date_ranges[0]
                    education['end_time'] = 'present'
            except Exception as e:
                print('education --> time ranges', e)
                education['start_time'] = ''
                education['end_time'] = ''
            item['education'].append(education)

        yield item
