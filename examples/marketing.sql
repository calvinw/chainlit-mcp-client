-- Create EmailCampaigns table
CREATE TABLE EmailCampaigns (
    campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_name TEXT NOT NULL,
    send_date TEXT NOT NULL,
    subject_line TEXT NOT NULL,
    emails_sent INTEGER NOT NULL,
    emails_opened INTEGER NOT NULL,
    clicks INTEGER NOT NULL
);

-- Insert data into EmailCampaigns table
INSERT INTO EmailCampaigns (campaign_name, send_date, subject_line, emails_sent, emails_opened, clicks) VALUES
('Summer Sale Launch', '2025-07-15 09:00:00', '🔥 Hot Deals Inside!', 1000, 350, 50),
('New Product Alert', '2025-07-22 14:30:00', '✨ Introducing Our Latest Item!', 1200, 400, 75),
('Loyalty Program', '2025-07-29 11:00:00', '🎁 Exclusive Rewards for You', 800, 500, 120),
('Back to School Savings', '2025-08-05 10:00:00', '🎒 Gear Up for Learning!', 1500, 600, 90),
('Fall Fashion Preview', '2025-08-12 16:00:00', '🍂 Sneak Peek at Fall Styles', 1100, 450, 65),
('Anniversary Sale - Day 1', '2025-08-19 08:30:00', '🎉 It''s Our Anniversary!', 2000, 800, 150),
('Anniversary Sale - Day 2', '2025-08-20 10:30:00', '🎁 More Anniversary Deals!', 1800, 700, 130),
('Weekend Coffee Promotion', '2025-08-23 09:30:00', '☕ Perfect Weekend Brews', 900, 300, 40),
('Limited Time Offer - Tech', '2025-08-26 15:00:00', '💻 Hot Tech Deals End Soon!', 1300, 550, 100),
('New Blog Post: Marketing Tips', '2025-09-02 11:30:00', '💡 Boost Your Marketing Today!', 1050, 400, 30),
('Holiday Gift Guide Preview', '2025-09-09 14:00:00', '🎄 Get Ready for the Holidays!', 1600, 650, 110),
('End of Season Clearance', '2025-09-16 09:15:00', '📉 Last Chance for Summer!', 1900, 750, 140),
('Special Discount for Members', '2025-09-23 12:00:00', '✨ Exclusive Savings Just for You', 1150, 500, 80),
('Flash Sale - 24 Hours Only', '2025-09-30 17:00:00', '⚡ Don''t Miss Out!', 1400, 600, 125),
('Welcome New Subscribers!', '2025-10-07 10:45:00', '👋 Thanks for Joining Us!', 700, 450, 25),
('Reminder: Loyalty Rewards', '2025-10-14 13:15:00', '🎁 Your Rewards Are Waiting!', 950, 550, 95),
('Early Bird Holiday Deals', '2025-10-21 09:45:00', '🦃 Beat the Holiday Rush!', 1700, 700, 135),
('Halloween Spooktacular Sale', '2025-10-28 16:30:00', '🎃 Treat Yourself to Savings!', 1250, 600, 115),
('Thanksgiving Week Offers', '2025-11-04 11:15:00', '🍁 Gratitude & Great Deals!', 1550, 700, 145),
('Cyber Monday is Coming!', '2025-11-11 14:45:00', '🚀 Get Ready to Save Big!', 2100, 900, 170);

-- Create WebsiteVisits table
CREATE TABLE WebsiteVisits (
    visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    visit_date TEXT NOT NULL,
    page_visited TEXT NOT NULL,
    visitor_type TEXT NOT NULL,
    source TEXT NOT NULL,
    campaign_id INTEGER,
    FOREIGN KEY (campaign_id) REFERENCES EmailCampaigns(campaign_id)
);

-- Insert data into WebsiteVisits table
INSERT INTO WebsiteVisits (visit_date, page_visited, visitor_type, source, campaign_id) VALUES
('2025-07-15 09:15:00', '/products', 'New', 'Email', 1),
('2025-07-15 09:20:00', '/product/abc', 'New', 'Email', 1),
('2025-07-15 10:00:00', '/', 'Returning', 'Organic Search', NULL),
('2025-07-22 14:40:00', '/new-arrivals', 'New', 'Email', 2),
('2025-07-22 14:45:00', '/product/xyz', 'New', 'Email', 2),
('2025-07-29 11:05:00', '/loyalty-program', 'Returning', 'Email', 3),
('2025-07-29 11:10:00', '/faq', 'Returning', 'Email', 3),
('2025-08-05 10:10:00', '/back-to-school', 'New', 'Email', 4),
('2025-08-05 10:15:00', '/products/backpacks', 'New', 'Email', 4),
('2025-08-12 16:10:00', '/fall-fashion', 'New', 'Email', 5),
('2025-08-19 08:35:00', '/anniversary-sale', 'New', 'Email', 6),
('2025-08-19 09:00:00', '/products/sale-items', 'Returning', 'Email', 6),
('2025-08-23 09:35:00', '/coffee', 'Returning', 'Email', 8),
('2025-08-26 15:05:00', '/tech-deals', 'New', 'Email', 9),
('2025-09-02 11:40:00', '/blog/marketing-tips', 'Returning', 'Email', 10),
('2025-09-09 14:05:00', '/holiday-gifts', 'New', 'Email', 11),
('2025-09-16 09:20:00', '/clearance', 'Returning', 'Email', 12),
('2025-09-23 12:05:00', '/member-discounts', 'Returning', 'Email', 13),
('2025-09-30 17:05:00', '/flash-sale', 'New', 'Email', 14),
('2025-07-16 11:00:00', '/about-us', 'Returning', 'Direct', NULL),
('2025-07-23 15:30:00', '/contact', 'New', 'Social Media', NULL),
('2025-08-06 12:45:00', '/products/toys', 'Returning', 'Paid Ads', NULL);

