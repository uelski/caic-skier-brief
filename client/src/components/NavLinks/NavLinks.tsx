import { NavLink } from "./NavLink";
import { Box, Group } from "@mantine/core";

const links = [
    { label: "", href: "https://github.com/uelski/caic-skier-brief", icon: "github-mark-white.png" },
    { label: "uelski.dev", href: "https://www.uelski.dev/" }
];

export function NavLinks() {
    return (
        <Group pr="md">
            {links.map((link) => (
                <Box key={link.href}>
                    <NavLink key={link.href} label={link.label} href={link.href} icon={link.icon} />
                </Box>
            ))}
        </Group>
    );
}